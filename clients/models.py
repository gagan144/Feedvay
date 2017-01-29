# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.db.models.fields.files import ImageFieldFile
from django_mysql import models as models57
from django.utils import timezone
import uuid, os, shortuuid, StringIO
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
import tinymce.models as tinymce_models
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from PIL import Image

from django.contrib.auth.models import User

from accounts.models import RegisteredUser
from utilities.theme import UiTheme, ColorUtils, render_skin

def upload_organization_logo_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/lg-{filename}".format(
        org_uid = str(instance.org_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_organization_icon_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/ic-{filename}".format(
        org_uid = str(instance.org_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_organization_theme_file_to(instance, filename):
    id = str(shortuuid.ShortUUID().random(length=10))
    fname, ext = os.path.splitext(filename)
    new_filename = "theme_{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/{filename}".format(
        org_uid = str(instance.org_uid),
        filename = new_filename #filename.replace(" ","_")
    )

class Organization(models57.Model):
    """
    An organization is an legal registered entity such as Company, Firm, Agency, Government or non-government organization, NGO etc.

    **State chart diagram for organization status**:

        .. image:: ../../_static/clients/organization_status_statechart.jpg

    **Points**:

        - **Status**:
            - ``frozen``: Means all operations of this organization have been ceased. No one can add update or create
            anything. Only viewing is allowed. This can be unfreeze to ``verified`` state.
            - ``deleted``: Means this organization has been permanently deleted from the system. It cannot be revived now.
        - Please call save after all transition method calls.
        - If verification fails, it is mandatory to provide reason. This reason will be shown to the user.
        - **Claims** on the organization can disabled if organization is known such as top organization or contracted clients. This can
          **ONLY** be done by staff user. Owner do not have rights to set this property.
        - To make changes in fields take care the following:
            - For Logo & icon dimensions & size constraints (must not change), make changes in
              LOGO_DIM, LOGO_MAX_SIZE etc in organization enums.
            - Make changes in :class:``market.forms.OrganizationCreateEditForm``.
            - Make changes for client side validations in '/static/partials/market/create_edit_organization.html'.
            - Make changes in 'market/templates/market/console/organization_settings.html'. Also in review modal.
            - Make updates in 'market.operations.*'.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    LOGO_DIM = (300, 100)
    LOGO_MAX_SIZE = 30*1024 # in bytes

    ICON_DIM = (64, 64)
    ICON_MAX_SIZE = 15*1024 # in bytes

    TYPE_PUBLIC = 'public'
    TYPE_PRIVATE = 'private'
    TYPE_GOV = 'government'
    TYPE_NGO = 'ngo'
    CH_TYPE = (
        (TYPE_PUBLIC, 'Public'),
        (TYPE_PRIVATE, 'Private'),
        (TYPE_GOV, 'Government'),
        (TYPE_NGO, 'NGO'),
    )

    ST_VERF_PENDING = 'verification_pending'
    ST_VERIFIED = 'verified'
    ST_VERF_FAILED = 'verification_failed'
    ST_FROZEN = 'frozen'
    ST_DELETED = 'deleted'
    CH_STATUS = (
        (ST_VERF_PENDING, 'Verification pending'),
        (ST_VERIFIED, 'Verified'),
        (ST_VERF_FAILED, 'Verification failed'),
        (ST_FROZEN, 'Frozen'),
        (ST_DELETED, 'Deleted')
    )

    # --- Fields ---
    org_uid     = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, help_text='Unique ID of an organization. This is mostly used in url in management console.')
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text='Name of the organization.')
    slug        = models.SlugField(unique=True, blank=True, db_index=True, editable=False, help_text='Slug of the name. Used in urls for public view.')
    acronym     = models.CharField(max_length=10, null=True, blank=True, help_text='Acronym of the organization if any.')

    # Settings
    description = models.TextField(max_length=512, help_text='Short description about the organization. Include keywords for better SEO and keep characters between 150-160.')
    type        = models.CharField(max_length=32, choices=CH_TYPE, help_text='Type of the organization.')
    logo        = models.ImageField(upload_to=upload_organization_logo_to, help_text='Organization logo of size 300x100 pixels.')
    icon        = models.ImageField(upload_to=upload_organization_icon_to, help_text='Organization icon of size 64x64 px.')

    # Customization
    # banner
    # splashscreen
    ui_theme    = models57.JSONField(default=None, blank=True, null=True, help_text="Custom UI theme for this organization. This must be of format 'utilities.theme.UiTheme'")
    theme_file  = models.FileField(upload_to=upload_organization_theme_file_to, editable=False, help_text='Theme file link which is automatically generated if ui_theme is defined')

    members     = models.ManyToManyField(RegisteredUser, through='OrganizationMember', help_text='Members of this organization.')

    # Statuses
    status      = FSMField(default=ST_VERF_PENDING, choices=CH_STATUS, protected=True, db_index=True, editable=False, help_text='Verification status of the organization.')
    failed_reason = tinymce_models.HTMLField(null=True, blank=True, help_text='Reason stating why this organization was failed during verification. This is shown to the user.')
    disable_claim = models.BooleanField(default=False, help_text='Set true to stop any further claims on this organization. Only staff can set this property, user cannot.')

    # Other
    staff_remarks = tinymce_models.HTMLField(null=True, blank=True, help_text='Remarks filled by staff. This can be related to anything such as user interaction for verification.')

    # Misc
    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this organization. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return "{}: {}".format(self.id, self.name)

    # --- Transitions ---
    @fsm_log_by
    @transition(field=status, source=ST_VERF_PENDING, target=ST_VERIFIED)
    def trans_verification_success(self, remarks=None):
        """
        Transition edge to transit organization status to verified.

        **Authors**: Gagandeep Singh
        """
        self.staff_remarks = remarks

    @fsm_log_by
    @transition(field=status, source=ST_VERF_PENDING, target=ST_VERF_FAILED)
    def trans_verification_failure(self, reason):
        """
        Transition edge for organization verification failed. A reason must be provided stating
        why verification was failed.

        **Authors**: Gagandeep Singh
        """
        self.failed_reason = reason

    @fsm_log_by
    @transition(field=status, source=ST_VERF_FAILED, target=ST_VERF_PENDING)
    def trans_revise_verification(self):
        """
        Transition edge to revise organization verification. This means organization has been edited and
        now again queued for verification.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_VERIFIED, target=ST_FROZEN)
    def trans_freeze(self):
        """
        Transition edge to freeze organization. This is done to cease all organization's operations.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_FROZEN, target=ST_VERIFIED)
    def trans_unfreeze(self):
        """
        Transition edge to unfreeze organization. This is done to restore all organization's operations.

        **Authors**: Gagandeep Singh
        """
        pass

    @fsm_log_by
    @transition(field=status, source=[ST_VERF_PENDING, ST_VERIFIED, ST_VERF_FAILED, ST_FROZEN], target=ST_DELETED)
    def trans_delete(self):
        """
        Transition edge to mark this organization as deleted. Use this method with caution.
        Once marked, all operations on the organization are stopped and everything is freezed.
        You cannot edit this organization and its entities however, you can view them.

        **Authors**: Gagandeep Singh
        """
        pass
    # --- /Transitions ---

    def update_theme_files(self, auto_save=True):
        """
        Method to update all theme files only if ui_theme is defined.

        :return: (bool) True if file was created and set to the field (irrespective of save), False if ui_theme was not set.

        **Authors**: Gagandeep Singh
        """
        if self.ui_theme:
            ui_theme = UiTheme(self.ui_theme)

            # render file
            content = render_skin(
                custom=True,
                clr_primary = ui_theme.primary,
                clr_prim_hover = ui_theme.primary_dark,
                clr_prim_disabled = ui_theme.primary_disabled
            )

            # Create InMemoryUploadObject
            f_io = StringIO.StringIO(content)
            mem_file_css = InMemoryUploadedFile(
                f_io,
                u'file',
                'theme.css',
                u'text/css',
                f_io.len,
                None
            )

            self.theme_file = mem_file_css

            if auto_save:
                self.save()

            return True
        else:
            return False

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Name slug
        if not self.slug:
            self.slug = slugify(self.name)

        # Images
        if not Organization.validate_logo_image(self.logo):
            raise ValidationError('Logo must be {}x{} and less than {} KB.'.format(
                Organization.LOGO_DIM[0],
                Organization.LOGO_DIM[1],
                Organization.LOGO_MAX_SIZE/1024
            ))
        if not Organization.validate_icon_image(self.icon):
            raise ValidationError('Icon must be {}x{} and less than {} KB.'.format(
                Organization.ICON_DIM[0],
                Organization.ICON_DIM[1],
                Organization.ICON_MAX_SIZE/1024
            ))

        # Check UI Theme
        if self.ui_theme is not None:
            if self.ui_theme == {}:
                self.ui_theme = None
            else:
                try:
                    theme_obj = UiTheme(self.ui_theme)
                except Exception as ex:
                    raise ValidationError("ui_theme: " + ex.message)

        # Status related validations
        if self.status == Organization.ST_VERF_FAILED and self.failed_reason in [None, '']:
            raise ValidationError("Please provide reason for verification failure.")

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()

        # Update theme
        if update_theme:
            # Theme errors have been checked in clean()
            self.update_theme_files(auto_save=False)

        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete an organization. Please use 'trans_delete()' method to mark this as deleted.")

    # ----- Static methods -----
    @staticmethod
    def generate_uitheme(primary_color):
        """
        Method to generate ui theme json wrapper :class:`utilities.theme.UiTheme`.

        :param primary_color: Primary color in hex format
        :return: :class:`utilities.theme.UiTheme` instance

        **Authors**: Gagandeep Singh
        """
        # from utilities.theme import UiTheme, ColorUtils
        return UiTheme(
            primary = primary_color,
            primary_dark = ColorUtils.scale_hex_color(primary_color, -40),
            primary_disabled = ColorUtils.scale_hex_color(primary_color, 60)
        )

    @staticmethod
    def does_exists(name):
        """
        Method to check if organization exists with given name or with slug of given name.

        :param name: Name of the organization
        :return: (bool) True if organization exists else False

        **Authors**: Gagandeep Singh
        """
        slug = slugify(name)
        return Organization.objects.filter(Q(name=name)|Q(slug=slug))

    @staticmethod
    def validate_logo_image(img_obj):
        """
        Method to validate organization logo image.
        Handles both ``InMemoryUploadedFile`` and ``ImageFieldFile`` objects.

        :param img_obj: InMemory object of image
        :return: True if image is valid

        **Authors**: Gagandeep Singh
        """
        if isinstance(img_obj, InMemoryUploadedFile):
            # InMemory object
            size = img_obj.size
            dim = Image.open(img_obj).size
        elif isinstance(img_obj, ImageFieldFile):
            # Django model field from ImageField
            size = img_obj._get_size()
            dim = img_obj._get_image_dimensions()

        return (size <= Organization.LOGO_MAX_SIZE and dim == Organization.LOGO_DIM)

    @staticmethod
    def validate_icon_image(img_obj):
        """
        Method to validate organization icon image.
        Handles both ``InMemoryUploadedFile`` and ``ImageFieldFile`` objects.

        :param img_obj: InMemory object of image
        :return: True if image is valid

        **Authors**: Gagandeep Singh
        """
        if isinstance(img_obj, InMemoryUploadedFile):
            # InMemory object
            size = img_obj.size
            dim = Image.open(img_obj).size
        elif isinstance(img_obj, ImageFieldFile):
            # Django model field from ImageField
            size = img_obj._get_size()
            dim = img_obj._get_image_dimensions()

        return (size <= Organization.ICON_MAX_SIZE and dim == Organization.ICON_DIM)


class OrganizationMember(models.Model):
    """
    Model to store members of an organization. This associates a user with his primary
    organization.

    **Uniqueness**: ``organization``, ``registered_user``

    **Authors**: Gagandeep Singh
    """
    organization    = models.ForeignKey(Organization, help_text='Associated organization.')
    registered_user = models.ForeignKey(RegisteredUser, db_index=True, help_text='User who is a memebr of the organization.')
    is_owner        = models.BooleanField(default=False, help_text='If true, it means this user is owner of this organization.')
    deleted         = models.BooleanField(default=False, editable=False, help_text="If true, it means user's membership is now removed.")

    created_on      = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on     = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('organization', 'registered_user')

    def __unicode__(self):
        return "{} <-> {}".format(self.organization.name, self.registered_user)

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
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete OrganizationMember record. Mark `delete' true instead.")


class OrgInvitation(models.Model):
    """
    Model to store all invitations made by the users of an organization to invite other users.
    An entry is made into this table before actually sending invitation message.

    **State chart diagram for organization status**:

        .. image:: ../../_static/clients/statechart_status_org_invitation.jpg

    **Points**:

        - A user can send invitation only in context of his organization. He cannot invite
          on behalf of the organization to which he does not belongs.
        - Incase, invitee is not present in the system, it must be first created before creating
          invitation record.
        - **Duplicity**: An invitation is said to be duplicate if as similar invitation exists with
          same organization, invitee and status is not equal to ``rejected`` or ``deleted``
          (i.e. ``new``, ``sent``, ``accepted`` invitations exists).
        - **Delete/Cancel**: To cancel an invitation, simply use ``trans_delete`` transition.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    ST_NEW = 'new'
    ST_SENT = 'sent'
    ST_ACCEPTED = 'accepted'
    ST_REJECTED = 'rejected'
    ST_DELETED = 'deleted'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_SENT, 'Sent'),
        (ST_ACCEPTED, 'Accepted'),
        (ST_REJECTED, 'Rejected'),
        (ST_DELETED, 'Deleted')
    )

    HIER_SIBLING = 'sibling'
    HIER_CHILD = 'child'
    CH_HIER_LINK = (
        (HIER_SIBLING, 'Sibling'),
        (HIER_CHILD, 'Child')
    )

    # --- Fields ---
    organization = models.ForeignKey(Organization, blank=True, editable=False, help_text='Organization to which invited user which attach.')
    invitee     = models.ForeignKey(RegisteredUser, related_name='invitee', editable=False, db_index=True, help_text='RegisteredUser who is invited.')
    org_hier_link = models.CharField(max_length=16, null=True, blank=True, default=None, editable=False, choices=CH_HIER_LINK, help_text='Relative attachment of invitee according to inviter in the org hierarchy. If None, means do not attach.')

    status      = FSMField(default=ST_NEW, choices=CH_STATUS, protected=True, db_index=True, editable=False, help_text='Status of the invitation.')
    delete_reason = tinymce_models.HTMLField(null=True, blank=True, editable=False, help_text="Reason for deletion incase status is 'deleted'.")

    inviter     = models.ForeignKey(RegisteredUser, editable=False, help_text='RegisteredUser who has invited other person.')
    created_on      = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on     = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        index_together = ('organization', 'inviter')

    def __unicode__(self):
        return "{} -> {}".format(self.inviter, self.invitee)

    # --- Transitions ---
    @transition(field=status, source=ST_NEW, target=ST_SENT)
    def trans_send(self):
        """
        Transition edge to send a new invitations.

        **Authors**: Gagandeep Singh
        """
        pass

    @transition(field=status, source=ST_SENT, target=ST_ACCEPTED)
    def trans_accept(self):
        """
        Transition edge to accept an invitation.

        **Authors**: Gagandeep Singh
        """
        pass

    @transition(field=status, source=ST_SENT, target=ST_REJECTED)
    def trans_reject(self):
        """
        Transition edge to reject an invitation.

        **Authors**: Gagandeep Singh
        """
        pass

    @transition(field=status, source=[ST_NEW, ST_SENT], target=ST_DELETED)
    def trans_delete(self, reason):
        """
        Transition edge to delete an invitation. Reason is required.

        **Authors**: Gagandeep Singh
        """
        self.delete_reason = reason
    # --- /Transitions ---

    def is_duplicate(self):
        """
        Method to check if similar invitation already exists or not.
        :return: True if exists else False.
        """
        if OrgInvitation.objects.filter(
            organization=self.organization, invitee=self.invitee
        ).exclude(status__in=[OrgInvitation.ST_REJECTED, OrgInvitation.ST_DELETED]).exists():
            return True
        else:
            return False

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        if self.pk is None:
            # New record
            # Check for duplicates
            if self.is_duplicate():
                raise ValidationError("Invitation already exists.")
        else:
            # Update modified date
            self.modified_on = timezone.now()

        # Validate inviter-organization
        try:
            inviter_org = OrganizationMember.objects.get(organization_id=self.organization.id, registered_user=self.inviter, deleted=False)
        except OrganizationMember.DoesNotExist:
            raise ValidationError("Inviter '{}' does not belongs to '{}'".format(self.inviter, self.organization.name))

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
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete invitation record. Instead use transition 'trans_delete'.")
