# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
from django.utils import timezone
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from mongoengine import signals as signals_mongo
import random, string, json, os

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField
from mongoengine.queryset import DoesNotExist as mongo_DoesNotExist

from django.conf import settings
from importlib import import_module
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in, user_logged_out
from fcm.models import AbstractDevice
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from accounts.exceptions import *
from owlery import owls

class RegisteredUser(models.Model):
    """
    Extension of django :class:`django.contrib.auth.models.User` model that maintains all public user
    information. For every public user, a record is created with reference to 'User' model along with
    other attributes such as mode of registration, user personal settings etc.

    **Points**:

        - This model does not include any staff users.
        - Username of these users is the mobile phone no with country code as prefix. Example: +919999999999
        - All login related process such as session allocation etc are done using traditional django 'User' model whereas
          other business related functionality are done using this model.
        - Detailed personal information are not kept in this model. It only contains basic information only such as name, email id.
        - Registration methods:

            - **Website** (Only one time): User can register directly on website using mobile no.
            - **Mobile app** (Multiple times): User can register using mobile app.
            - **Enterprise app** (Only one time): Passive registration of the user that is automatically created as a **lead** while using enterprise app.
              The account remains inactive until user register himself manually using any of the methods. Only one time record is created
              and ignore in further cases.

            For registration flow, refer the document.
        - Registration can be multiple times. Only last registration information is kept for now.


    **State chart diagram for user status**:

        .. image:: ../../_static/accounts/registereduser_statechart.jpg

    .. warning::
        This model must not trigger any update to django 'User' model since it can trigger model's save.
        However, you can update this model without any intervention of 'User' model.

    **Authors**: Gagandeep Singh
    """

    # ----- enums -----
    REG_WEB_PORTAL = 'web_portal'
    REG_MOBILE = 'mobile_app'
    REG_CAPTURED_LEAD = 'captured_lead' # User was captured as lead while from enterprise app.
    CH_REG_METHOD = (
        (REG_WEB_PORTAL, 'Web portal'),
        (REG_MOBILE, 'Mobile app'),
        (REG_CAPTURED_LEAD, 'Captured lead'),
    )

    ST_LEAD = 'lead'
    ST_VERIFICATION_PENDING = 'verification_pending'
    ST_VERIFIED = 'verified'
    CH_STATUS = (
        (ST_LEAD, 'Lead'),
        (ST_VERIFICATION_PENDING, 'Verification pending'),
        (ST_VERIFIED, 'Verified')
    )

    # ----- fields -----
    user        = models.OneToOneField(User, db_index=True, editable=False, help_text='Reference to django user model.')
    reg_method  = models.CharField(max_length=32, choices=CH_REG_METHOD, db_index=True, editable=False, help_text='Last registration method used by the user')
    reg_count   = models.SmallIntegerField(default=1, editable=False, help_text='No of times this user registered himself.')
    last_reg_date = models.DateTimeField(auto_now_add=True, editable=False, help_text='Last registration datetime.')
    status      = FSMField(protected=True, default=ST_LEAD, choices=CH_STATUS, db_index=True, editable=False, help_text='Status of user registration.')

    # Permissions, Roles and DataAccess with context to Organizations
    superuser_in = models.ManyToManyField('clients.Organization', blank=True, help_text='Organizations in which this user has all permissions and data access. This overrides roles, permissions & data acess.')
    roles       = models.ManyToManyField('OrganizationRole', blank=True, help_text='Organizational roles for this user.')
    permissions = models.ManyToManyField(Permission, through='UserPermission', blank=True, help_text='Organizational permissions for this user.')
    # data access through query

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this user was made.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def profile(self):
        return UserProfile.objects.get(registered_user_id=self.id)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ('-created_on', )

    # ----- Transitions -----
    @fsm_log_by
    @transition(field=status, source=[ST_LEAD, ST_VERIFIED], target=ST_VERIFICATION_PENDING)
    def trans_registered(self):
        """
        User has registered. Status is transitioned from ``lead`` to ``verification_pending``.
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_VERIFICATION_PENDING, target=ST_VERIFIED)
    def trans_verification_completed(self):
        """
        User has verified himself. Status is transitioned from ``verification_pending`` to ``verified``.
        """
        pass

    # ----- /Transitions -----

    # --- Password ---
    def set_password(self, new_password, send_owls=True):
        """
        Method to set a registered user password and save it.
        This also sends any owls (Email or SMS) if required. Any owls related errors are silently ignored.

        :param new_password: New password
        :param send_owls: Set True to send mail/SMS to the user. Default:True
        :return: None

        .. note::
            To prevent logout, execute following after this function.

                >>> auth.update_session_auth_hash(request, user)


        .. warning::
            This method does not confirm with old password. Please confirm old password
            before changing as per your use case for security reasons.

        **Authors**: Gagandeep Singh
        """
        user = self.user
        user.set_password(new_password)
        user.save()

        if send_owls:
            # Send all owls
            # (a) SMS owl
            owls.SmsOwl.send_password_change_success(
                mobile_no = user.username,
                username = user.username
            )

            # (b) Email owl
            owls.EmailOwl.send_password_change_success(user)

        # TODO: Logout user from all mobile devices

    # ----- Permissions & access -----
    def get_perm_cache_key(self, organization):
        """
        Method to return permission cache key. This method only generates key and does not
        affect cache.

        :param organization: Organization for which key is to be generated.
        :return: Cache key
        """
        return "{}__{}".format(self.user.username, organization.id)

    def fetch_all_permissions(self, organization, update_cache=True):
        """
        Method to fetch all user permissions for an organization from database and cache it if instructed.

        :param organization: :class:`clients.models.Organization` instance
        :param update_cache: If true, this will cache permission json in default cache with key as '<username>__<org.id>'
            and expiry as :py:data:`settings.SESSION_COOKIE_AGE_PUBLIC`.
        :return: Permissions JSON or {} if user does not belongs to the organization.

        **Permission JSON format**:

        .. code-block:: json

            {
                "<app-label>.<model-name>"{
                    "permissions": ["add_<model-name>", "view_<model-name>", "change_<model-name>", "delete_<model-name>"],
                    "data_access": {

                    }
                },

            }

        **data_access structure in permission JSON**:

            - ``None``: No data access allowed on corresponding model
            - ``{}``: All/complete access allowed on records of corresponding model in that organization
            - data_access is only filled for those model are in permission json


        **Authors**: Gagandeep Singh
        """

        # --- Check membership ---
        if organization.organizationmember_set.filter(registered_user_id=self.id, deleted=False).exists():
            # --- User is a member of the organization ---

            # Check if he is a superuser

            if self.superuser_in.filter(id=organization.id).exists():
                # --- User is SUPERUSER ---
                # file_path = os.path.join(os.path.dirname(__file__), 'data/superuser.json')
                # with open(file_path, 'r') as f:
                #     perm_json = json.load(f)
                from accounts.utils import get_superuser_perm_json
                perm_json = get_superuser_perm_json()

                # Set/Update cache
                if update_cache:
                    CACHE_KEY = self.get_perm_cache_key(organization)
                    cache.set(CACHE_KEY, perm_json, settings.SESSION_COOKIE_AGE_PUBLIC)

                return perm_json
                # --- /User is SUPERUSER ---
            else:
                # --- Fetch permissions ---
                KEY_PERMISSIONS = "permissions"
                KEY_DATA_ACCESS = "data_access"

                gen_app_n_model = lambda app_label, model_name: "{}.{}".format(app_label, model_name)

                perm_json = {}

                # (a) User direct permissions
                list_perm = Permission.objects.filter(
                    userpermission__organization_id = organization.id,
                    userpermission__registered_user_id = self.id
                )

                for perm in list_perm:
                    # Check app-model
                    app_n_model = gen_app_n_model(perm.content_type.app_label, perm.content_type.model)
                    if not perm_json.has_key(app_n_model):
                        perm_json[app_n_model] = {
                            KEY_PERMISSIONS: [],
                            KEY_DATA_ACCESS: None
                        }

                    # Set Param codename
                    perm_code = perm.codename
                    if not perm_json[app_n_model][KEY_PERMISSIONS].__contains__(perm_code):
                        perm_json[app_n_model][KEY_PERMISSIONS].append(perm_code)


                # (b) On the basis of roles
                list_perm = Permission.objects.filter(
                    organizationrole__organization_id = organization.id,
                    organizationrole__registereduser = self
                )

                for perm in list_perm:
                    # Check app-model
                    app_n_model = gen_app_n_model(perm.content_type.app_label, perm.content_type.model)
                    if not perm_json.has_key(app_n_model):
                        perm_json[app_n_model] = {
                            KEY_PERMISSIONS: [],
                            KEY_DATA_ACCESS: None
                        }

                    # Set Param codename
                    perm_code = perm.codename
                    if not perm_json[app_n_model][KEY_PERMISSIONS].__contains__(perm_code):
                        perm_json[app_n_model][KEY_PERMISSIONS].append(perm_code)

                # (c) Data access
                list_data_access = UserDataAccess.objects.filter(
                    organization_id = organization.id,
                    registered_user_id = self.id
                )

                for da in list_data_access:
                    app_n_model = gen_app_n_model(da.content_type.app_label, da.content_type.model)
                    if perm_json.has_key(app_n_model):
                        perm_json[app_n_model][KEY_DATA_ACCESS] = {} if da.all_access else da.access_filter


                # Set/Update cache
                if update_cache:
                    CACHE_KEY = self.get_perm_cache_key(organization)
                    cache.set(CACHE_KEY, perm_json, settings.SESSION_COOKIE_AGE_PUBLIC)

                return perm_json
                # --- /Fetch permissions ---
        else:
            # --- User is NOT a member the organization ---
            return {}




    def get_data_access(self, organization):
        """
        Method to get all data access for this user in an organization.

        :param organization: Organization for which data access is to be fetch.
        :return: List<:class:`accounts.models.UserDataAccess`>

        **Authors**: Gagandeep Singh
        """
        qry = self.userdataaccess_set.filter(organization_id=organization.id)
        return qry

    def get_all_permissions(self, organization):
        """
        Method to get all user permissions for an organization first from **cache**. If not found,
        fetch all permissions from database, cache it and return permission json as in ``fetch_all_permissions()``.

        :param organization: Orgnization for which permissions are to be obtained.
        :return: Permission JSON

        **Authors**: Gagandeep Singh
        """

        CACHE_KEY = self.get_perm_cache_key(organization)

        perm_json = cache.get(CACHE_KEY)
        if perm_json is None:
            perm_json = self.fetch_all_permissions(organization, update_cache=True)

        return perm_json

    def delete_permission_cache(self, organization=None):
        """
        Delete permission cache of this user for all organizations

        :param organization: (Optional) If provided, only permission cache for this org is deleted.
        :return: Count of cache key deleted

        **Authors**: Gagandeep Singh
        """
        qry = self.organizationmember_set.all()
        if organization is not None:
            qry = qry.filter(organization_id=organization.id)

        count = 0
        for org_mem in qry.select_related('organization'):
            cache_key = self.get_perm_cache_key(org_mem.organization)
            cache.delete(cache_key)
            count += 1

        return count

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

            # Delete all his organization's permission cache
            self.delete_permission_cache()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # Override delete method to prevent record deletion.
        raise ValidationError('You cannot delete RegisteredUser.')

    @staticmethod
    def construct_username(country_tel_code, mobile_no):
        """
        Static method to create actual database username by concatenating
        country telephone code and 10-digit mobile number

        :param country_tel_code: Country telephone code
        :param mobile_no: 10-digit mobile number
        :return: Actual username; '<country_tel_code>+<mobile_no>'

        **Authors**: Gagandeep Singh
        """
        return "{}-{}".format(country_tel_code, mobile_no)

    @staticmethod
    def deconstruct_username(country_tel_code, actual_username):
        """
        Static method to obtain 10-digit mobile number from actual username by removing
        country telephone code from actula username.

        :param country_tel_code: Country telephone code
        :param actual_username: '<country_tel_code>+<mobile_no>'
        :return: 10-digit mobile number

        **Authors**: Gagandeep Singh
        """

        return actual_username.replace("{}-".format(country_tel_code), "")


class UserToken(models.Model):
    """
    Model to store tokens issued to a registered user for various purposes such as registration.

    **Points**:

        - Uniqueness of a token is based on :class:`accounts.model.RegisteredUser` and purpose.
        - Tokens are only issued to registered user.
        - Token can be overridden for same user & purpose. This is possible when the same process is again executed.
        - No audit trail is maintained for a token. Present is the only truth.
        - Token must be deleted after use or will be automatically deleted after they cross their expiry date.

    .. note::
        Tokens are not user sessions.

    **Authors**: Gagandeep Singh
    """

    PUR_REG_VERF = 'reg_verification'
    PUR_EMAIL_VERIF = 'email_verification'
    PUR_PASS_RESET = 'password_reset'
    CH_PURPOSE = (
        (PUR_REG_VERF, 'Registration Verification'),
        (PUR_EMAIL_VERIF, 'Email verification'),
        (PUR_PASS_RESET, 'Password Reset'),
    )

    registered_user = models.ForeignKey(RegisteredUser, db_index=True, editable=False, help_text='Reference to the registered user to whom this token belongs.')
    purpose     = models.CharField(max_length=64, choices=CH_PURPOSE, db_index=True, editable=False, help_text='Purpose for which this token is issued')

    value       = models.CharField(max_length=512, editable=False, help_text='Value of the token')
    expire_on   = models.DateTimeField(editable=False, db_index=True, help_text='Date after which this token will expire.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, help_text='Date on which this token was issued.')

    def __unicode__(self):
        return "{} - {}".format(self.registered_user.user.username, self.purpose)

    class Meta:
        unique_together = ('registered_user', 'purpose')

    def humanize_expire_on(self, format):
        return self.expire_on.time().strftime(format)     #TODO: Timezone: convert to local

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Set expiry date
        if self.purpose in [UserToken.PUR_REG_VERF, UserToken.PUR_EMAIL_VERIF, UserToken.PUR_PASS_RESET]:
            self.value = UserToken.gen_verification_otp()
            self.expire_on = timezone.now() + timezone.timedelta(seconds=settings.VERIFICATION_EXPIRY)

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    @staticmethod
    def gen_verification_otp():
        charset = string.digits
        return ''.join(random.sample(charset,6))

    @staticmethod
    def verify_user_token(username, purpose, value):
        """
        Static method to verify token given a username and value.

        :param username: Actual username
        :param purpose: Purpose of the token. One of the ``UserToken.CH_PURPOSE``
        :param value: Value of the token
        :return: True (for pass) and False (if failed)

        Raises :class:`accounts.exceptions.InvalidRegisteredUser` Exception incase registered user not found.

        **Authors**: Gagandeep Singh
        """
        try:
            registered_user = RegisteredUser.objects.get(user__username=username)

            now = timezone.now()
            least_date = now - timezone.timedelta(seconds=settings.VERIFICATION_EXPIRY)

            try:
                # Get & verify user token
                user_token = UserToken.objects.filter(
                    registered_user = registered_user,
                    purpose = purpose,

                    value = value,
                    expire_on__gte = least_date,
                )[0]

                return True
            except IndexError:
                return False

        except RegisteredUser.DoesNotExist:
            raise InvalidRegisteredUser()

# ---------- User Sessions ----------
class UserSession(models.Model):
    """
    Model to link user to its session. Currently, django does not provide direct linking of
    user to its sessions. On login, a session is created and send session_id to the browser
    in the cookie, which is received back in the request from where server resolve session.
    So, there is no way to find all sessions of a user.

    This model keeps a track of session and its user. Whenever a user logs in, django fires
    a 'logged in' signal which is captured and an entry is made with user and session key.

    .. note:
        There can be multiple sessions for a user.

    **Authors**: Gagandeep Singh
    """

    user        = models.ForeignKey(User, db_index=True, help_text='Reference to the user.')
    session_id  = models.CharField(max_length=40, db_index=True, help_text='Session id (key). This is not a foriegn key since session model can be shifted to different database.')

    @property
    def session(self):
        return Session.objects.get(session_key=self.session_id)

    def __unicode__(self):
        return self.session_id

# --- User signal handlers ---
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    User login signal handler that creates an entry in :class:`accounts.model.UserSession` to
    map the session to current user.

    Here session has already been created, hence it can be easily accessed from ``request.session``.

    **Authors**: Gagandeep Singh
    """
    UserSession.objects.get_or_create(
        user = user,
        session_id = request.session.session_key
    )

def user_logged_out_handler(sender, request, user, **kwargs):
    """
    User logout signal handler that deletes user-session entry from :class:`accounts.model.UserSession`.

    **Authors**: Gagandeep Singh
    """

    # Get session key from request.session
    session_key = request.session.session_key

    if session_key:
        try:
            UserSession.objects.get(user=user, session_id=session_key).delete()
        except:
            pass

user_logged_in.connect(user_logged_in_handler)
user_logged_out.connect(user_logged_out_handler)

# ---------- User Claims ----------
class UserClaim(models.Model):
    """
    Model to record all claims by registered user on various entities such as
    organization, brands, POBS etc.

    **Points**:

        - Only :class:`accounts.models.RegisterUser` can make a claim.
        - Claim cannot be made on disabled entities.
        - If an entity's claim is disabled after being claimed, all claims are automatically rejected.
          Claim permission on entity can only be disabled by staff.
        - Remark is necessary when claim is rejected.
        - Scoring is automatically updated for the user when status changes.
        - This model automatically sends owls on status update.

    **Statechart diagram for claim status**:

        .. image:: ../../_static/accounts/user_claim_statechart.jpg

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    ENTITY_BRAND = 'brand'
    CH_ENTITY = (
        (ENTITY_BRAND, 'Brand'),
    )

    ST_NEW = 'new'
    ST_ACCEPTED = 'accepted'
    ST_REJECTED = 'rejected'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_ACCEPTED, 'Accepted'),
        (ST_REJECTED, 'Rejected')
    )

    # --- Fields ---
    registered_user = models.ForeignKey(RegisteredUser, db_index=True, editable=False, help_text='Registered user who made a claim.')
    entity      = models.CharField(choices=CH_ENTITY, max_length=32, editable=False, help_text='Entity class on which claim has been made.')
    entity_id   = models.IntegerField(editable=False, help_text='Entity model instance id which is being claimed.')
    status      = FSMField(default=ST_NEW, protected=True, db_index=True, editable=False, help_text='Status of the claim.')

    remarks     = models.TextField(null=True, blank=True, help_text='Remarks related to this claim. Required when claim is rejected.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which claim was made.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this claim was modified.')

    class Meta:
        unique_together = ('registered_user', 'entity', 'entity_id')

    def __unicode__(self):
        return "{} - {}:{}".format(self.registered_user, self.entity, self.entity_id)

    # ----- Transitions -----
    @fsm_log_by
    @transition(field=status, source=ST_NEW, target=ST_ACCEPTED)
    def trans_approved(self):
        """
        Claim has been found genuine and has been accepted. Call this after everything has been processed.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_NEW, target=ST_REJECTED)
    def trans_disapproved(self):
        """
        Claim was found false. Call this after everything has been processed.

        **Authors**: Gagandeep Singh
        """
        pass

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Verify entity being claimed
        if self.entity == UserClaim.ENTITY_BRAND:
            from market.models import Brand
            try:
                brand = Brand.objects.get(id=int(self.entity_id))
                if not self.pk and brand.disable_claim:
                    # Check only for new claim; Brand claim can be disabled after a claim.
                    raise ValidationError("Brand with id '{}' cannot be claimed.".format(self.entity_id))

            except Brand.DoesNotExist:
                raise ValidationError("Brand with id '{}' does not exists.".format(self.entity_id))

        # Remarks check
        if self.status == UserClaim.ST_REJECTED and (self.remarks is None or self.remarks == ''):
            raise ValidationError("Please provide a remark for rejecting this claim.")

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

# ---------- User Devices ----------
class UserDevice(AbstractDevice):
    """
    Model to keep track of user devices that have registered for
    **Google Firebase Cloud Messaging (FCM)**. This model is specific for FCM only and might
    not be applicable for other push notification services.

    For every user's (not registered user) device and entry is created. Using this, query can be made
    to obtain list of devices to those message is to be send.

    .. note::
        This model links :class:`django.contrib.auth.models.User` and not :class:`accounts.models.RegisteredUser`.
        This is done to allow provision for staff user to also register their devices for push notifications.

    **Authors**: Gagandeep Singh
    """
    user    = models.ForeignKey(User, db_index=True, help_text='User to which this device belongs to.')

    def __unicode__(self):
        return "{} - {}".format(self.user.username, self.dev_id)

# ---------- MongoDb models ----------

class UserProfile(Document):
    """
    Mongodb model to store registered user information. This model includes wide variety
    of user related attributes.

    **Attribute organisation**:
    User attributes and their values are organised in two ways; dictionary and list. This is done
    to provide query optimization for wide use cases.

        1. **Dictionary**: Attributes are maintained as key-value pair in a dictionary field **'attributes'**.
           Use this field for quick value lookup mostly when attribute name is known. Also in case of
           report display, use this field to get attribute values.

                - Contains only currently active attributes for the user.
                - Read-only field. Do not write/delete inside this field. It is overridden by save().
                - This field is **not indexed**, since dictionary indexing does not perform well.
                - So, **NEVER** use this field for complex query, aggregations or map-reduce.

        2. **List of objects**: Attributes are also maintained in form of list of objects in the field **'list_attributes'**,
           with each object in the list representing one attribute having information such as name, value as well as
           other meta information such as active, last updated on etc.

                - Contains all active & inactive fields.
                - Save uses this field to populate **'attributes'** field.
                - This field is **indexed** on name, value & active field of the objects across all documents in UserProfile.
                - Always use this field for complex queries and aggregation.
                - While using **MongoDb aggregation framework**, unwind **list_attributes** before aggregating.
                - **Map-Reduce** might not take good advantage of this field since unwind is not available for MongoDb M-R.

    **Adding/updating new attribute**:

        Always add or update attribute using **'list_attributes'** field only. **DO NOT** use 'attributes' field.
        This is because save function will truncate 'attributes' field, loop over 'list_attributes' and add only active
        attributes to 'attributes' field.

        Use of ``add_update_attribute()`` is recommended.

    **Deleting attribute**:

        Always use 'list_attributes' field but **NEVER** delete any entry. TO delete an attribute, mark that attribute
        as ``active=False``. Save function will automatically remove it from 'attributes' field.
        To revive an attribute, override its value and mark ``active=True``.

        Use of ``delete_attribute()`` is recommended.

    **Mandatory attributes**:

        All attributes in **UserAttributes** embedded document tagged as ``required=True`` are mandatory and must be
        present in 'list_attributes'. Model will not save until all required fields have values.

    **When this model is created/updated**:

        This model is created only during registration process and updated each time :class:`accounts.models.RegisteredUser` is saved.

    **Triggers and effects**:

        This model migrates all changes in set of fields defined in ``USER_MODEL_FIELDS`` to :class:``django.contrib.auth.models.User`
        model on attribute update or delete. This is done in ``save()`` method.

    **Authors**: Gagandeep Singh
    """

    # --- Enums ---
    # These are list of fields whos values are migrated to 'User' model on change.
    USER_MODEL_FIELDS = [
        'first_name',
        'last_name',
        'email'
    ]

    # --- Embedded Documents ---
    class DetailedAttribute(EmbeddedDocument):
        """
        Mongodb embedded document to store an attribute in detail. This not only includes attribute name and value,
        but also other meta information such as active, last_updated_on etc.

        .. warning::
            Do not delete this record. Simply mark active as false.

        **Authors**: Gagandeep Singh
        """
        name        = StringField(required=True, help_text="Name of the attribute.")
        value       = BaseField(required=True, help_text="Value of the attribute. This can be of any data type.")

        active      = BooleanField(required=True, default=True, help_text="Whether this attribute is active or not. Set False in case od delete.")
        locked      = BooleanField(required=True, default=False, help_text="If True attribute cannot be updated or deleted.")
        verified    = BooleanField(required=True, default=False, help_text="Flag to indicate if this information is verified or not.")
        remarks     = StringField(required=False, default=None, help_text='Remarks for this attributes such as verification remarks.')
        last_updated_on = DateTimeField(required=True, default=timezone.now, help_text="Date on which this record was last updated.")

        def __unicode__(self):
            return "{} : {}".format(self.name, self.value)


    class UserAttributes(EmbeddedDocument):
        """
        Mongodb embedded document for :class:`accounts.models.UserProfile` model.
        It is this document that stores user attributes in key-value pairs.

        .. note::
            Use this model for quick lookup for attribute value. These keys will not be indexed
            so **DO NOT** use them in queries.

        .. warning::
            Following attributes will be replaced by that in :class:`django.contrib.auth.models.User` model:

                - first_name
                - last_name

        **Authors**: Gagandeep Singh
        """

        # --- Enums ---
        GEN_MALE = 'male'
        GEN_FEMALE = 'female'
        GEN_OTHER = 'other'
        CH_GENDER = (
            (GEN_MALE, 'Male'),
            (GEN_FEMALE, 'Female'),
            (GEN_OTHER, 'Other')

        )

        BLOOD_O_P = 'O+'
        BLOOD_O_N = 'O-'
        BLOOD_A_P = 'A+'
        BLOOD_A_N = 'A-'
        BLOOD_B_P = 'B+'
        BLOOD_B_N = 'B-'
        BLOOD_AB_P = 'AB+'
        BLOOD_AB_N = 'AB-'
        CH_BLOOD_GROUP = (
            (BLOOD_O_P, BLOOD_O_P),
            (BLOOD_O_N, BLOOD_O_N),
            (BLOOD_A_P, BLOOD_A_P),
            (BLOOD_A_N, BLOOD_A_N),
            (BLOOD_B_P, BLOOD_B_P),
            (BLOOD_B_N, BLOOD_B_N),
            (BLOOD_AB_P, BLOOD_AB_P),
            (BLOOD_AB_N, BLOOD_AB_N)
        )

        # --- Fields ---
        first_name      = StringField(required=True, help_text="First name of the user. This will be updated by 'first_name' in User model.")
        last_name       = StringField(required=True, help_text="Last Name of the user. This will be updated by 'last_name' in User model.")

        gender          = StringField(required=False, choices=CH_GENDER, help_text="User gender.")  # OPTIONAL SINCE gender might not be present during invitation.
        date_of_birth   = DateTimeField(required=False, help_text="Date of birth (with time as 00:00:00.00+0000)")  # OPTIONAL since dob might not be present during invitation.
        email           = EmailField(required=False, help_text="Email address. This must be same as 'email' in User model.")

        blood_group     = StringField(choices=CH_BLOOD_GROUP, help_text="Blood group of the user.")
    # --- /Embedded Documents ---

    # ------ UserProfile Fields ------
    registered_user_id  = IntField(required=True, unique=True, help_text="Instance ID of :class:`accounts.models.RegisteredUser`.")

    attributes          = EmbeddedDocumentField(UserAttributes, help_text="Dictionary of user attributes and values. These are not indexed.")
    list_attributes     = EmbeddedDocumentListField(DetailedAttribute, help_text="List of atrributes along with their meta details. These are indexed.")

    created_on          = DateTimeField(required=True, default=timezone.now, help_text='Date on which this record was created.')
    modified_on         = DateTimeField(default=None, help_text="Date on which this record was modified.")

    meta = {
        "index_cls": False,
        "indexes":[
            "registered_user_id",
            "-modified_on",

            "list_attributes.name",
            "list_attributes.value",
            "list_attributes.active",
        ]
    }

    @property
    def registered_user(self):
        return RegisteredUser.objects.get(id=self.registered_user_id)


    def __unicode__(self):
        return "{} - {} {}".format(self.registered_user_id, self.attributes.first_name, self.attributes.last_name)


    # --- Attributes management ---
    def add_update_attribute(self, name, value, auto_save=True):
        """
        Method to add new attribute if it does not exists or update an attribute if it is not locked.
        An attribute will automatically be revived if found inactive.

        :param name: Name of the attribute.
        :param value: Value for that attribute.
        :param auto_save: True to write to db after addition else False
        :return: Bool tuple (is_new, updated) 'is_new': True if attribute was created. 'updated': True if action was success else False

        **Note**: Throws 'ValidationError' if attribute is locked

        **Authors**: Gagandeep Singh
        """

        # Check for valid attribute name
        allowed_names = UserProfile.UserAttributes._fields.keys()
        if name not in allowed_names:
            raise ValidationError("Inavlid attribute name '{}'. Allowed names: {}".format(name, allowed_names))

        # Find attribute existences
        is_new = True
        updated = False
        for attr in self.list_attributes:
            if attr.name == name:
                is_new = False
                if attr.locked:
                    raise ValidationError("Denied! Attribute '{}' is locked.".format(name))

                attr.value = value
                attr.active = True
                attr.last_updated_on = timezone.now()

                updated = True
                break

        if is_new:
            self.list_attributes.append(
                UserProfile.DetailedAttribute(
                    name = name,
                    value = value,
                    active = True,
                )
            )
            updated = True

        # Save
        if updated and auto_save:
            self.save()

        return (is_new, updated)


    def delete_attribute(self, name, auto_save=True):
        """
        Method to delete an attribute, that is mark attribute active as false.
        An already deleted (inactive) attribute will again be marked inactive.

        :param name: Name of the attribute
        :param auto_save: True to write to db after deletion else False
        :return: Bool tuple (found, updated)

        **Note**: Throws 'ValidationError' if attribute is locked

        **Authors**: Gagandeep Singh
        """

        found = False
        updated = False
        for attr in self.list_attributes:
            if attr.name == name:
                found = True
                if attr.locked:
                    raise ValidationError("Denied! Attribute '{}' is locked.".format(name))

                attr.active = False

                updated = True
                break

        # Save
        if found and updated and auto_save:
            self.save()

        return (found, updated)

    def lock_attribute(self, name, auto_save=True):
        """
        Method to lock an attribute. Locking an attribute will prevent any updation or deletion of an attribute.

        :param name: Name of the attribute.
        :param auto_save: Save model after locking
        :return: True if attribute found and successfully locked else False

        **Authors**: Gagandeep Singh
        """

        updated = False
        for attr in self.list_attributes:
            if attr.name == name:
                attr.locked = True

                updated = True
                break

        if updated and auto_save:
            self.save()

        return updated


    def unlock_attribute(self, name, auto_save=True):
        """
        Method to unlock an attribute and release it from locked state.

        :param name: Name of the attribute
        :param auto_save: Save model after unlocking
        :return: True if attribute found and successfully released else False

        **Authors**: Gagandeep Singh
        """

        updated = False
        for attr in self.list_attributes:
            if attr.name == name:
                attr.locked = False

                updated = True
                break

        if updated and auto_save:
            self.save()

        return updated

    def mark_attribute_verification(self, name, is_verified, remarks, auto_save=True):
        """
        Method to mark an attribute verified or unverified.
        This method can change ``verified`` value of an attribute even if it is locked.

        :param name: Name of the attribute
        :param is_verified: (bool) True if mark attribute as verified else False
        :param remarks: Remarks for verification
        :return: Tuple (found, updated)

        **Authors**: Gagandeep Singh
        """

        if not isinstance(is_verified, bool):
            raise Exception("'is_verified' must be a boolean.")

        found = False
        updated = False
        for attr in self.list_attributes:
            if attr.name == name:
                found = True
                attr.verified = is_verified

                updated = True
                break

        # Save
        if found and updated and auto_save:
            self.save()

        return (found, updated)

    def get_meta_dict(self):
        """
        Method that returns dictionary of nested objects with key as attribute name and
        value as dictionary object containing information for that attribute.
        :return: Dictionary of format {"<attribute_name">: { <information dict> },  }
        """

        meta_dict = {}
        for attr in self.list_attributes:
            data = dict(attr.to_mongo())
            if isinstance(data['value'], timezone.datetime):
                data['value'] = data['value'].isoformat()
            meta_dict[attr.name] = data

        return meta_dict


    def save(self, complete_save=True, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        # Check for RegisteredUser
        # This will throw DoesNotExist exception
        try:
            reg_user = self.registered_user

            # Modify modified_on date-time
            if self.pk:
                self.modified_on = timezone.now()

            # Set 'attributes' based on 'list_attributes'
            # For all attributes in 'list_attributes' that are active, copy them in the dict 'attributes'
            dict_attr = {}
            for attr in self.list_attributes:
                if attr.active:
                    dict_attr.update({attr.name: attr.value})
            self.attributes = UserProfile.UserAttributes(**dict_attr)

            return super(self.__class__, self).save(*args, **kwargs)
        except RegisteredUser.DoesNotExist:
            raise Exception('RegisterdUser with id={} does not exists.'.format(self.registered_user_id))

    def delete(self, **write_concern):
        # Override delete method to prevent record deletion.
        raise ValidationError('Denied! You cannot delete UserProfile.')

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """
        Post-save method for UserProfile mongo model.

        **Authors**: Gagandeep Singh
        """

        # Migrate all user model changes to User model
        user = RegisteredUser.objects.get(id=document.registered_user_id).user

        save_user = False
        for fieldname in UserProfile.USER_MODEL_FIELDS:
            val = document.attributes[fieldname]

            if fieldname == 'email' and val is None:
                val = ''

            if val != getattr(user, fieldname):
                setattr(user, fieldname, val)
                save_user = True

        if save_user:
            user.save()

signals_mongo.post_save.connect(UserProfile.post_save, sender=UserProfile)

# ----- User Permissions, Roles and Data Access -----
class UserPermission(models.Model):
    """
    Model to associate user with permissions for an organization.
    This model only defines what action a user is allowed on an entity. This **does not**
    specifies on which instances of the entity user can perform that action.

    **Points**:

        - All user permissions are defined under organization to which he is part of.
        - Currently permissions are applied on database entities only (not pages).
        - To get list of permissions on entities we use :class:`django.contrib.auth.models.Permission`.
        - Each permission relates to one of the CRUD operation allowed on that entity.
        - **Uniqueness**: ``organization``, ``registered_user``, ``permission`` i.e under an organization,
          a user can have only one permission for an action (CRUD) over an entity.

    **Authors**: Gagandeep Singh
    """
    organization = models.ForeignKey('clients.Organization', help_text='Organization under which permission is granted.')
    registered_user = models.ForeignKey(RegisteredUser, help_text='User to which permission is to be applied.')
    permission  = models.ForeignKey(Permission, help_text='Permission allowing action on that entity.')

    created_by  = models.ForeignKey(User, editable=False, help_text='User who assigned this permission.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('organization', 'registered_user', 'permission')

    def __unicode__(self):
        return str(self.id)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Pre-delete method for this model.

        **Authors**: Gagandeep Singh
        """
        # Clear permission cache the user
        self.registered_user.delete_permission_cache(self.organization)

        super(self.__class__, self).delete(using, keep_parents)

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model.

        **Authors**: Gagandeep Singh
        """

        # Clear permission cache the user
        instance.registered_user.delete_permission_cache(instance.organization)

post_save.connect(UserPermission.post_save, sender=UserPermission)

class OrganizationRole(models.Model):
    """
    Organization roles are a generic way of categorizing users to apply permissions. A user can belong to
    any number of roles. Use role when you want to assign similar set of permission to group
    of users.

    **Points**:

        - This model does not specifies data access. Only set of permissions.
        - All roles are defined under an organization.
        - **Uniqueness**: ``organization``, ``name``

    **Authors**: Gagandeep Singh
    """
    organization = models.ForeignKey('clients.Organization', help_text='Organization in which this role can be used for users.')
    name        = models.CharField(max_length=128, help_text='Name of the role.')
    permissions = models.ManyToManyField(Permission, help_text='Permissions that belongs to this role.')

    created_by  = models.ForeignKey(User, editable=False, help_text='User who created this role.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('organization', 'name')
        permissions = (
            ("view_organizationrole", "Can view organization role"),
        )

    def __unicode__(self):
        return "{} ({})".format(self.name, self.organization.name)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model.

        **Authors**: Gagandeep Singh
        """

        # Clear permission cache for all users who has this role
        if kwargs['created'] == False:
            org = instance.organization
            for reg_user in instance.registereduser_set.all():
                cache_key = reg_user.get_perm_cache_key(org)
                cache.delete(cache_key)

post_save.connect(OrganizationRole.post_save, sender=OrganizationRole)

class UserDataAccess(models57.Model):
    """
    Model to define what instances of an entity a user is allowed to perform actions.
    Where, UserPermissions and Roles together specify set of action a user to allowed on
    an entity, this model specifies sets of instances on which user can perform those actions.

    **Points**:

        - Instances are specified in terms of actual django orm query filters and not mostly list
          of instance pk. These filters are in form of JSON as per the underline database (MySQL or MongoDb)
        - To allow access over all instances, set ``all_access`` to True. This will ignore ``access_filter``.
        - If ``all_access`` is ``False``, ``access_filter``` is mandatory.
        - **Uniqueness**: ``organization``, ``registered_user``, ``content_type`` i.e. only one entry
          for user in an organization that hass access over an entity.


    **Authors**: Gagandeep Singh
    """
    organization    = models.ForeignKey('clients.Organization', help_text='Organization of which entities are accessible.')
    registered_user = models.ForeignKey(RegisteredUser, help_text='User who has access to the instances.')
    content_type    = models.ForeignKey(ContentType, help_text='Entity to which instances belongs to.')
    all_access      = models.BooleanField(default=False, help_text='If true, ``access_filter`` is ignored and access is granted over all instances.')
    access_filter   = models57.JSONField(default=None, blank=True, null=True, help_text='JSON query filter to filter instance on which access is granted.')

    created_by  = models.ForeignKey(User, editable=False, help_text='User who granted this data aceess.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('organization', 'registered_user', 'content_type')
        verbose_name_plural = 'User data accesses'

    def __unicode__(self):
        return "{}".format(self.id)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        if self.all_access is False and (self.access_filter in [None, {}]):
            raise ValidationError("Please specify access filter.")

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model.

        **Authors**: Gagandeep Singh
        """

        # Clear permission cache the user
        instance.registered_user.delete_permission_cache(instance.organization)

post_save.connect(UserDataAccess.post_save, sender=UserDataAccess)

# ----- /User Permissions, Roles and Data Access -----


# ---------- Global Methods ----------
def force_logout_user(user_id):
    """
    Method to forcefully logout a user from all web login only.
    Technically, this method finds all session references of a user from :class:`accounts.models.UserSession`.
    and delete them from SessionStore one-by-one.

    :param user_id: User object id
    :return: Number of deleted sessions from SessionStore

    **Authors**: Gagandeep Singh
    """

    # Get all UserSession
    list_user_sessions = UserSession.objects.filter(user_id=user_id)

    count = 0
    # If there are any session
    if len(list_user_sessions):
        # Get SessionStore. This can be the same db or some other db (redis).
        engine = import_module(settings.SESSION_ENGINE)
        _SessionStore = engine.SessionStore

        # loop over all user sessions
        for user_session in list_user_sessions:
            # Get actual session instance by creating SessionStore object using session key
            session = _SessionStore(user_session.session_id)

            # Delete session from store
            session.delete()

            count += 1

        # Delete all UserSession
        list_user_sessions.delete()

    return count
