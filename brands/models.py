# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals


from django.db import models
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

from accounts.models import RegisteredUser

class Brand(models.Model):
    """
    Model to capture brand details. A brand is a broad term that includes all types of brands,
    company, firm, business name etc. A brand groups one or more *Point Of Business and Service (POBS)* under one
    common name.

    This model also includes various customizations for a brand.

    **Points**:

        - Brand cannot be active if it is not verified. However when verified, brand can be marked as
          active or inactive.
        - If verification fails, it is mandatory to provide reason. This reason will be shown to the user.

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
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text='Name of the brand.')
    description = models.TextField(max_length=512, help_text='Short description about the brand. Include keywords for better SEO and keep characters between 150-160.')

    owners      = models.ManyToManyField(through=BrandOwner, help_text='Owners of this brand.')

    # Customization
    # logo
    # icon
    # banner
    # splashscreen
    # theme_colors = JOSN


    status      = FSMField(default=ST_VERF_PENDING, choices=CH_STATUS, protected=True, db_index=True, editable=False, help_text='Verification status of brand.')
    failed_reason = models.TextField(null=True, blank=True, help_text='Reason stating why this brand was failed during verification. This is shown to the user.')
    active      = models.BooleanField(default=False, db_index=True, help_text='Whether this brand is active or not. This remains false until status is verified. ')
    disable_claim = models.BooleanField(default=False, help_text='Set true to stop any further claims on this brand. Use this for top known brands or contracted clients.')

    created_by  = models.ForeignKey(User, help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Status relate validations
        if self.status == Brand.ST_VERF_FAILED and self.failed_reason in [None, '']:
            raise ValidationError("Please provide reason for verification failure.")

        if self.status != Brand.ST_VERIFIED and self.active:
            raise ValidationError("Brand cannot be active until it is verified.")

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


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