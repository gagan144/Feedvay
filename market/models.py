# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField

from django.contrib.auth.models import User

from accounts.models import RegisteredUser

# ---------- Business or Service Point ----------
class BusinessServicePoint(models57.Model):
    """
    Business or Service Point (BSP) is a generic term that refers to place where consumer
    can consume a product or can be offered with a service. Such a place can be a business point
    where a person sells a product or conducts operations or runs his business. This can
    also be a place that is offered a service.

    Examples:
        Local business shop such as restaurants, clothing, repair shop, grocery shop etc,
        Government office, post boxes, ATMs, Company office, pan wala shop, chemist, hospital,
        Tutor, Coaching center, mobile app/website lets say to order food or buy products and so on.

    **Points**:

        - BSP can be physical (Place/Person) or virtual (Website/App).
        - Each BSP has its unique id.
        - Each BSP is associated with one type that defines its attributes.
          Type cannot be changed once selected.
        - Attributes are not kept in this table. Instead are placed in mongodb collection.
        - This model only includes basic fields that are mostly used for entity relationships.

    **Authors**: Gagandeep Singh
    """

    bsp_code    = models.CharField(max_length=255, unique=True, db_index=True, help_text='Unique id of the BSP. This will be shared with public.')
    name        = models.CharField(max_length=255, db_index=True, help_text='Name of the BSP. This can be duplicate.')
    slug        = models.SlugField(unique=True, blank=True, db_index=True, help_text='Slug of the name used for url referencing.')

    description = models.TextField(max_length=512, null=True, blank=True, help_text='Description about the BSP. Include keywords for better SEO and keep characters between 150-160.')

    # type        = models
    # organisation    =
    # brand         =
    members      = models.ManyToManyField(RegisteredUser, help_text='People who manages this BSP. These can be owners or compant employee.')

    # Controls
    active      = models.BooleanField(default=True, db_index=True, help_text='Control to temporarly hide BSP if set false.')
    # status

    # Misc
    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this BSP. This can be registered user or staff user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def profile(self):
        return BspProfile.objects.get(bsp_id=str(self.id))

    class Meta:
        ordering = ('name', )


    def clean(self):
        """
        Method to clean & valida-te data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Name slug
        if not self.slug:
            self.slug = slugify(self.name)

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        raise ValidationError("You cannot delete a BSP. Mark it inactive instead.")


class BspProfile(Document):
    """
    Mongodb collection to capture BSP attributes & characteristics. This stores all
    information about BSP.

    **Points**:

        - ``name``, ``slug``, ``status`` field is updated automatically from :class:`market.models.BusinessServicePoint`.

    **Authors**: Gagandeep Singh
    """

    # --- Embedded documents ---
    class Attribute(EmbeddedDocument):
        """
        Mongodb embedded document to store BSP attribute.

        **Authors**: Gagandeep Singh
        """
        name    = StringField(required=True, help_text='Name of the attribute.')
        value   = BaseField(required=True, help_text='Value of the attribute.')

        def __unicode__(self):
            return self.name

    class SocialMedia(EmbeddedDocument):
        """
        Mongodb embedded document to store link to social media pages of BSP.

        **Authors**: Gagandeep Singh
        """
        facebook    = URLField(help_text='Link to facebook page.')
        twitter     = URLField(help_text='Link to twitter page.')

    # --- Enums ---
    ST_OPN_OPEN = 'open'
    ST_OPN_COMING_SOON = 'comming_soon'
    ST_OPN_CLOSED = 'closed'
    ST_OPEN_REMOVED = 'removed'
    CH_OPEN_STATUS = (
        (ST_OPN_OPEN, 'Open'),
        (ST_OPN_COMING_SOON, 'Coming Soon'),
        (ST_OPN_CLOSED, 'Closed'),
        (ST_OPEN_REMOVED, 'Removed'),
    )

    # --- Fields ---
    bsp_id      = StringField(required=True, unique=True, help_text='Instance id of :class:`market.models.BusinessServicePoint`.')
    name        = StringField(required=True, help_text="Name as in BusinessServicePoint. This is updated from instance. Do not change here.")
    slug        = StringField(required=True, unique=True, help_text="Slug as in BusinessServicePoint. This is updated from instance. Do not change here.")

    # Attributes
    attributes  = DictField(required=True, help_text='Attributes of BSP according to BspType. Use this for reporting or display.')
    avg_rating  = FloatField(default=None, help_text="Average rating.")
    list_attributes = EmbeddedDocumentListField(Attribute, required=True, help_text="List of attributes. These are populated by 'attributes' so do not update here. Use this for analytics.")

    # Contact
    emails      = ListField(help_text='Email ids')
    website     = URLField(help_text='Website url if any.')

    # Statuses
    verification_status = StringField(required=True, help_text='Verification status of the BSP.')
    open_status = StringField(required=True, default=ST_OPN_OPEN, choices=CH_OPEN_STATUS, help_text='Open status of BSP.')

    # Misc
    tags        = ListField(help_text='Tags related to this BSP.')
    social      = EmbeddedDocumentField(SocialMedia, help_text='Social media page links.')
    other_details = StringField(help_text='Any details regarding this BSP.')

    # Dates
    created_on  = DateTimeField(default=timezone.now, required=True, help_text='Date on which this record was created in the database.')
    modified_on = DateTimeField(default=None, help_text='Date on which this record was modified.')

    meta = {
        'indexes':[
            'bsp_id',
            'name'
        ]
    }


    def save(self, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            self.modified_on = timezone.now()

        return super(BspProfile, self).save(*args, **kwargs)