# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals


from django.db import models
from django.db.models import Q
from django.db.models.fields.files import ImageFieldFile
from django.template.defaultfilters import slugify
from django_mysql.models import JSONField
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import StringIO
import os
from django.core.files.uploadedfile import InMemoryUploadedFile,SimpleUploadedFile
from PIL import Image
import tinymce.models as tinymce_models
from django_mysql import models as models57

from accounts.models import RegisteredUser
from utilities.theme import UiTheme, render_skin

def upload_brand_logo_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "brands/{brand_uid}/lg-{filename}".format(
        brand_uid = str(instance.brand_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_brand_icon_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "brands/{brand_uid}/ic-{filename}".format(
        brand_uid = str(instance.brand_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_brand_theme_file_to(instance, filename):
    return "brands/{brand_uid}/{filename}".format(
        brand_uid = str(instance.brand_uid),
        filename = filename.replace(" ","_")
    )

class Brand(models.Model):
    """
    Model to capture brand details. A brand is a broad term that includes all types of brands,
    company, firm, business name etc. A brand groups one or more *Point Of Business and Service (POBS)* under one
    common name.

    This model also includes various customizations for a brand.

    **Points**:

        - Brand has status in context to it authenticity.
            - **Unverified** brands remains operational but are not publically shown.
            - **Failed** brands are not operational and are not shown to the public.
            - **Verified** brands have no restrictions.
        - Brand can be **active** or inactive. It cannot be active if it is not verified. However when verified, activeness can be toggled.
        - Brand cannot be deleted. To **delete** brand,change status to ``deleted``. A brand can be marked any time.
        - If verification fails, it is mandatory to provide reason. This reason will be shown to the user.
        - **Claims** on the brand can disabled if brand is known such as top brands or contracted clients. This can
          **ONLY** be done by staff user. Owner do not have rights to set this property.
        - To make changes in fields take care the following:
            - For Logo & icon dimensions & size constraints (must not change), make changes in
              LOGO_DIM, LOGO_MAX_SIZE etc in brand enums.
            - Make changes in :class:``brands.forms.BrandCreateEditForm``.
            - Make changes for client side validations in '/static/partials/brands/create_edit_brand.html'.
            - Make changes in 'brands/templates/brands/console/brand_settings.html'. Also in review modal.
            - Make updates in 'brands.operations.*'.


    **State chart diagram for brand status**:

        .. image:: ../../_static/brands/brand_status_statechart.jpg

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    LOGO_DIM = (300, 100)
    LOGO_MAX_SIZE = 30*1024 # in bytes

    ICON_DIM = (64, 64)
    ICON_MAX_SIZE = 15*1024 # in bytes

    ST_VERF_PENDING = 'verification_pending'
    ST_VERIFIED = 'verified'
    ST_VERF_FAILED = 'verification_failed'
    ST_DELETED = 'deleted'

    CH_STATUS = (
        (ST_VERF_PENDING, 'Verification pending'),
        (ST_VERIFIED, 'Verified'),
        (ST_VERF_FAILED, 'Verification failed'),
        (ST_DELETED, 'Deleted')
    )

    # --- Fields ---
    brand_uid   = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, help_text='Unique ID of a brand which are hard to guess and can be used in urls. ')
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text='Name of the brand.')
    slug        = models.SlugField(unique=True, blank=True, db_index=True, help_text='Slug of the name used for url referencing and dedupe matching.')
    acronym     = models.CharField(max_length=10, null=True, blank=True, help_text='Acronym of the brand.')
    description = models.TextField(max_length=512, help_text='Short description about the brand. Include keywords for better SEO and keep characters between 150-160.')

    owners      = models.ManyToManyField(RegisteredUser, through='BrandOwner', help_text='Owners of this brand.')

    # Customization
    logo        = models.ImageField(upload_to=upload_brand_logo_to, help_text='Brand logo of size 300x100 pixels.')
    icon        = models.ImageField(upload_to=upload_brand_icon_to, help_text='Brand icon of size 64x64 px.')
    # banner
    # splashscreen
    ui_theme    = JSONField(default=None, blank=True, null=True, help_text="Custom UI theme for this brand. This must be of format 'utilities.theme.UiTheme'")
    theme_file  = models.FileField(upload_to=upload_brand_theme_file_to, editable=False, help_text='Theme file link which is automatically generated if ui_theme is defined')

    # Status
    status      = FSMField(default=ST_VERF_PENDING, choices=CH_STATUS, protected=True, db_index=True, editable=False, help_text='Verification status of brand.')
    failed_reason = models.TextField(null=True, blank=True, help_text='Reason stating why this brand was failed during verification. This is shown to the user.')
    staff_remarks = tinymce_models.HTMLField(null=True, blank=True, help_text='Remarks filled by staff. This can be related to anything such as user interaction for verification.')
    active      = models.BooleanField(default=False, db_index=True, help_text='Switch to disable brand temporarly. Configurations/editting can be made however, brand does not appear to public.')
    disable_claim = models.BooleanField(default=False, help_text='Set true to stop any further claims on this brand. Only staff can set this property, user cannot.')

    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return "{}: {}".format(self.id, self.name)


    # --- Transitions ---
    @fsm_log_by
    @transition(field=status, source=ST_VERF_PENDING, target=ST_VERIFIED)
    def trans_verified(self, remarks=None):
        """
        Transition edge to transit brand status to verified.

        **Authors**: Gagandeep Singh
        """
        self.active = True
        self.staff_remarks = remarks

    @fsm_log_by
    @transition(field=status, source=ST_VERF_PENDING, target=ST_VERF_FAILED)
    def trans_verification_failed(self, reason):
        """
        Transition edge for brand verification failed. A reason must be provided stating
        why this brand was failed.

        **Authors**: Gagandeep Singh
        """
        self.active = False
        self.failed_reason = reason

    @fsm_log_by
    @transition(field=status, source=ST_VERF_FAILED, target=ST_VERF_PENDING)
    def trans_revise_verification(self):
        """
        Transition edge to revise brand verification. This means brand has been editted and
        now again queued for verification.

        **Authors**: Gagandeep Singh
        """
        self.active = False

    @fsm_log_by
    @transition(field=status, source=[ST_VERF_PENDING, ST_VERIFIED, ST_VERF_FAILED], target=ST_DELETED)
    def trans_delete(self):
        """
        Transition edge to mark this brand as deleted. Use this method with caution.
        Once marked, all operations on the brand are stopped and everything is freezed.
        You cannot edit this brand and its entities however, you can view them.

        Deleted brand is not shown to the public.

        **Authors**: Gagandeep Singh
        """
        pass

    # --- /Transitions ---

    # --- Owner management ---
    def add_owner(self, reg_user):
        """
        Method to add new registered user as owner to this brand.
        :param reg_user: :class:`accounts.models.RegisteredUser` instance
        :return: :class:`brands.models.BrandOwner` instance if successfully created.

        Throws exception: IntegrityError if user is already an owner.

        **Authors**: Gagandeep Singh
        """
        ownership = BrandOwner.objects.create(
            brand = self,
            registered_user = reg_user
        )

        return ownership

    def delete_owner(self, reg_user, send_owls=True):
        """
        Method to disassociate (delete) a registered user from brand ownership.

        :param reg_user: :class:`accounts.models.RegisteredUser` instance of the user giving awya the ownership
        :param send_owls: Set True if you want to send owls.

        Throws exception: DoesNotExist(BrandOwner) if user is not an owner of this brand.

        **Owls send**:

            - **To disassociated user**: SMS, Email
            - **To other owners**: Email, Notification

        **Authors**: Gagandeep Singh
        """

        # Delete owner
        BrandOwner.objects.get(brand=self, registered_user=reg_user).delete()

        if send_owls:
            # --- Send all owls ---
            from owlery import owls

            # (a) Send to released user
            owls.SmsOwl.send_brand_disassociation_success(reg_user.user.username, self, reg_user.user.username)
            owls.EmailOwl.send_brand_disassociation_success(reg_user.user, self)

            # (b) send notification and email to all remaining owners of the brand
            owls.EmailOwl.send_brand_partner_left_message(self, reg_user)
            owls.NotificationOwl.send_brand_partner_left_notif(self, reg_user)


    # --- /Owner management ---

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
        if not Brand.validate_logo_image(self.logo):
            raise ValidationError('Logo must be {}x{} and less than {} KB.'.format(
                Brand.LOGO_DIM[0],
                Brand.LOGO_DIM[1],
                Brand.LOGO_MAX_SIZE/1024
            ))
        if not Brand.validate_icon_image(self.icon):
            raise ValidationError('Icon must be {}x{} and less than {} KB.'.format(
                Brand.ICON_DIM[0],
                Brand.ICON_DIM[1],
                Brand.ICON_MAX_SIZE/1024
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
        if self.status == Brand.ST_VERF_FAILED and self.failed_reason in [None, '']:
            raise ValidationError("Please provide reason for verification failure.")

        if self.status != Brand.ST_VERIFIED and self.active:
            raise ValidationError("Brand cannot be active until it is verified.")

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
        raise ValidationError("You cannot delete a brand. Please use 'trans_delete()' method to mark this marked as deleted.")

    # ----- Static methods -----
    @staticmethod
    def generate_uitheme(primary_color):
        """
        Method to generate ui theme json wrapper :class:`utilities.theme.UiTheme`.
        :param primary_color: Primary color in hex format
        :return: :class:`utilities.theme.UiTheme` instance
        """
        from utilities.theme import UiTheme, ColorUtils
        return UiTheme(
                primary = primary_color,
                primary_dark = ColorUtils.scale_hex_color(primary_color, -40),
                primary_disabled = ColorUtils.scale_hex_color(primary_color, 60)
            )


    @staticmethod
    def does_exists(name):
        """
        Method to check if brand exists with given name or with slug of given name.

        :param name: Name of the brand
        :return: (bool) True if brand exists else False

        **Authors**: Gagandeep Singh
        """
        slug = slugify(name)
        return Brand.objects.filter(Q(name=name)|Q(slug=slug))

    @staticmethod
    def validate_logo_image(img_obj):
        """
        Method to validate brand logo image.
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

        return (size <= Brand.LOGO_MAX_SIZE and dim == Brand.LOGO_DIM)

    @staticmethod
    def validate_icon_image(img_obj):
        """
        Method to validate brand icon image.
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

        return (size <= Brand.ICON_MAX_SIZE and dim == Brand.ICON_DIM)



class BrandOwner(models.Model):
    """
    Model to store brand owners. A brand owner is a super user with all permissions and roles for that brand as well
    entities below that brand in hierarchy. These entities can be people, POBS etc.

    **Points**:

        - Brand-RegisteredUser association must be unique. A registered user can be associated with multiple brands.
        - Entry in this model signifies that registered user is an owner of the brand
        - **Disassociation**: To remove a user ownership, simply delete entry in this model.

    **Authors**: Gagandeep Singh
    """

    brand           = models.ForeignKey(Brand, db_index=True, on_delete=models.CASCADE, help_text='Associated brand in the ownership.')
    registered_user = models.ForeignKey(RegisteredUser, db_index=True, on_delete=models.CASCADE, help_text='Associated registered user in the ownership.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('brand', 'registered_user')

    def __unicode__(self):
        return "{} <-> {}".format(self.brand.name, self.registered_user)


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

class BrandChangeRequest(models57.Model):
    """
    Model to log all brand change requests made by the owners.

    **Points**:

        - Change request can be made by brand owner himself or any registered user that has
          permissions to change brand information.
        - Record is logged only when brand status is ``verified``. In other cases, changes are directly
          reflected in the brand model since they have to be verified and there is no need to log
          separate entry.
        - This model is **not audit trail** of the brand.
        - Change request is **atomic**. That means, a change is only migrated if and only if
          all changes in the brand fields are found valid. In case, any field value change is found
          incorrect or invalid, entire request is rejected and user must request again with valid data.
        - In case of rejection, reason is mandatory.

    .. warning::
        This model is **not audit** trail for :class:`brands.models.Brand` model. This only logs
        changes requested by the user and migrate it Brand model after acceptance.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    ST_NEW = 'new'
    ST_SUCCESS = 'success'
    ST_REJECTED = 'rejected'
    ST_OUTDATED = 'outdated'
    CH_STATUS =(
        (ST_NEW, 'New'),
        (ST_SUCCESS, 'Success'),
        (ST_REJECTED, 'Rejected'),
        (ST_OUTDATED, 'Outdated')
    )

    # --- Fields ---
    brand       = models.ForeignKey(Brand, db_index=True, editable=False, help_text='Brand for which change is logged.')
    registered_user = models.ForeignKey(RegisteredUser, db_index=True, editable=False, help_text='Registered user that made the request. This can be a owner or permissioned user.')

    data_changes = JSONField(editable=False, help_text="Change request data in JSON form. These are mapped to 'Brand' model.")

    status      = models.CharField(max_length=16, default=ST_NEW, choices=CH_STATUS, help_text='Status of this request.')
    remarks     = tinymce_models.HTMLField(null=True, blank=True, help_text='Reason for rejecting this request. This is shown to the user.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('-created_on',)

    def __unicode__(self):
        return "{} - {}".format(self.brand.name, self.id)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.brand.status != Brand.ST_VERIFIED:
            raise ValidationError('You can log changes for verified brand only.')

        if self.status == BrandChangeRequest.ST_REJECTED:
            if self.remarks in [None, '']:
                raise ValidationError('Please provide rejection reason.')

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
        raise ValidationError("You cannot delete a change request. Mark it outdated instead.")