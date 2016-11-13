# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
import random
import string

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField
from mongoengine.queryset import DoesNotExist as mongo_DoesNotExist

from django.conf import settings
from importlib import import_module
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in, user_logged_out

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

    # ----- fields -----
    user        = models.OneToOneField(User, db_index=True, editable=False, help_text='Reference to django user model.')
    reg_method  = models.CharField(max_length=32, choices=CH_REG_METHOD, db_index=True, editable=False, help_text='Last registration method used by the user')
    reg_count   = models.SmallIntegerField(default=1, editable=False, help_text='No of times this user registered himself.')
    last_reg_date = models.DateTimeField(auto_now_add=True, editable=False, help_text='Last registration datetime.')
    status      = FSMField(default=ST_LEAD, protected=True, db_index=True, editable=False, help_text='Status of user registration.')

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
        Post save trigger for this model. This will be called after the record has
        been created or updated.

        **Authors**: Gagandeep Singh
        """

        # Update 'UserProfile' only if this exists
        # Cannot create here because during registration, when 'RegisteredUser' is created this routine will not
        # have date of birth, gender etc since they are not present in 'User' model.
        # Update here make surety that User.<attributes> are same as UserProfile.<attributes>
        try:
            user = instance.user

            user_profile = UserProfile.objects.get(registered_user_id=instance.id)
            user_profile.add_update_attribute('first_name', user.first_name, auto_save=False)
            user_profile.add_update_attribute('last_name', user.last_name, auto_save=False)
            user_profile.save()

        except mongo_DoesNotExist:
            pass

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
post_save.connect(RegisteredUser.post_save, sender=RegisteredUser)


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
    PUR_PASS_RESET = 'password_reset'
    CH_PURPOSE = (
        (PUR_REG_VERF, 'Registration Verification'),
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
        if self.purpose in [UserToken.PUR_REG_VERF, UserToken.PUR_PASS_RESET]:
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


    **Authors**: Gagandeep Singh
    """

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

        gender          = StringField(required=True, choices=CH_GENDER, help_text="User gender.")
        date_of_birth   = DateTimeField(required=True, help_text="Date of birth (with time as 00:00:00.00+0000)")
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