# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals


from django.db import models
from django_mysql.models import JSONField
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile,SimpleUploadedFile

from accounts.models import RegisteredUser
from utilities.theme import UiTheme, render_skin

def upload_brand_logo_to(instance, filename):
    return "brands/{brand_uid}/logo__{filename}".format(
        brand_uid = str(instance.brand_uid),
        filename = filename.replace(" ","_")
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
        - Brand cannot be deleted. To **delete** brand, mark it ``deleted``. A brand can be marked deleted at any status or time.
        - If verification fails, it is mandatory to provide reason. This reason will be shown to the user.
        - **Claims** on the brand can disabled if brand is known such as top brands or contracted clients.

    **State chart diagram for brand status**:

        .. image:: ../../_static/brands/brand_status_statechart.jpg

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    ST_VERF_PENDING = 'verification_pending'
    ST_VERIFIED = 'verified'
    ST_VERF_FAILED = 'verification_failed'

    CH_STATUS = (
        (ST_VERF_PENDING, 'Verification pending'),
        (ST_VERIFIED, 'Verified'),
        (ST_VERF_FAILED, 'Verification failed')
    )

    # --- Fields ---
    brand_uid   = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, help_text='Unique ID of a brand which are hard to guess and can be used in urls. ')
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text='Name of the brand.')
    description = models.TextField(max_length=512, help_text='Short description about the brand. Include keywords for better SEO and keep characters between 150-160.')

    owners      = models.ManyToManyField(RegisteredUser, through='BrandOwner', help_text='Owners of this brand.')

    # Customization
    logo        = models.ImageField(upload_to=upload_brand_logo_to, help_text='Brand logo of size 300x100 pixels.')
    # icon
    # banner
    # splashscreen
    ui_theme    = JSONField(default=None, blank=True, null=True, help_text="Custom UI theme for this brand. This must be of format 'utilities.theme.UiTheme'")
    theme_file  = models.FileField(upload_to=upload_brand_theme_file_to, editable=False, help_text='Theme file link which is automatically generated if ui_theme is defined')

    # Status
    status      = FSMField(default=ST_VERF_PENDING, choices=CH_STATUS, protected=True, db_index=True, editable=False, help_text='Verification status of brand.')
    failed_reason = models.TextField(null=True, blank=True, help_text='Reason stating why this brand was failed during verification. This is shown to the user.')
    active      = models.BooleanField(default=False, db_index=True, help_text='Switch to disable brand temporarly. Configurations/editting can be made however, brand does not appear to public.')
    deleted     = models.BooleanField(default=False, db_index=True, help_text='If true, it means this brand has been deleted. All operations are stopped from now. Brand does not appears to public. This must be used rarely.')
    disable_claim = models.BooleanField(default=False, help_text='Set true to stop any further claims on this brand. Use this for top known brands or contracted clients.')

    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    def __unicode__(self):
        return "{}: {}".format(self.id, self.name)

    def mark_deleted(self):
        """
        Method to mark this brand deleted. Use this method with caution.
        Caution! Once marked, all operations on the brand are stopped and everything is freezed.
        You cannot edit this brand and its entities however, you can view them.

        Deleted brand is not shown to the public.

        **Authors**: Gagandeep Singh
        """

        self.deleted = True
        self.save()

    # --- Transitions ---
    @fsm_log_by
    @transition(field=status, source=ST_VERF_PENDING, target=ST_VERIFIED)
    def trans_verified(self):
        """
        Transition edge to transit brand status to verified.

        **Authors**: Gagandeep Singh
        """
        self.active = True

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

    def delete_owner(self, reg_user):
        """
        Method to disassociate (delete) a registered user from brand ownership.

        :param reg_user: :class:`accounts.models.RegisteredUser` instance

        Throws exception: DoesNotExist(BrandOwner) if user is not an owner of this brand.

        **Authors**: Gagandeep Singh
        """

        BrandOwner.objects.get(brand=self, registered_user=reg_user).delete()

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

        # Check UI Theme
        if self.ui_theme is not None:
            if self.ui_theme == {}:
                self.ui_theme = None
            else:
                try:
                    theme_obj = UiTheme(self.ui_theme)
                except Exception as ex:
                    raise ValidationError("ui_theme: " + ex.message)

        # Status relate validations
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
        raise ValidationError("You cannot delete a brand. Please use 'mark_deleted()' method to mark this marked as deleted.")


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

    brand           = models.ForeignKey(Brand, db_index=True, help_text='Associated brand in the ownership.')
    registered_user = models.ForeignKey(RegisteredUser, db_index=True, help_text='Associated registered user in the ownership.')

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