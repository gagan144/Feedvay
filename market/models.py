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
from utilities.abstract_models.mongodb import AddressEmbDoc, ContactEmbDoc

# ----- General -----
class BspTag(Document):
    """
    Mongodb collection to store various tag for all types of BSP.

    **Authors**: Gagandeep Singh
    """
    name    = StringField(required=True, max_length=64, unique=True, help_text='Name of the tag. These will be visible to users.')
    list_bsp_types = ListField(required=True, help_text='List of BSP on which this type will be applicable.')
    active  = BooleanField(required=True, default=True, help_text="If false, this tag will not be visible. Deactive will not affect associated BSPs.")

    meta = {
        'ordering': 'name',
        'indexes':[
            'name',
            'list_bsp_types'
        ]
    }

    def __unicode__(self):
        return self.name

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """
        self.list_bsp_types = list(set(self.list_bsp_types))
        return super(BspTag, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        raise ValidationError("You cannot delete a BSP tag. Instead mark 'active' as false.")

# ----- BSP related models -----
class RestaurantCuisine(models.Model):
    """
    Model to store various types of restaurant cuisines.

    **Authors**: Gagandeep Singh
    """
    name    = models.CharField(max_length=64, unique=True, db_index=True, help_text='Name/title of the cuisines.')
    active  = models.BooleanField(default=True, db_index=True, help_text='If false, this will not be visible. Deactivating will not affect currently associated restaurants.')

    class Meta:
        ordering = 'name'

    def __unicode__(self):
        return self.name

    def delete(self, **write_concern):
        raise ValidationError("You cannot delete a restaurant cuisines. Instead mark 'active' as false.")


# ---------- Business or Service Point ----------
class BusinessServicePoint(Document):
    """
    Business or Service Point (BSP) is a generic term that refers to place/person/thing where consumer
    can consume a product or can be offered with a service. Such a place can be a business point
    where a person sells a product or conducts operations or runs his business. This can
    also be a place that offers any kind of service. Moreover, it can also be person such as a teacher.

    Examples:
        Local business shop such as restaurants, clothing, repair shop, grocery shop etc,
        Government office, post boxes, ATMs, Company office, pan wala shop, chemist, hospital,
        Tutor, Coaching center, mobile app/website lets say to order food or buy products and so on.

    **Points**:

        - Each BSP has its unique id.
        - Each BSP is associated with one type that defines its attributes.
          Type cannot be changed once selected.
        - Field ``list_attributes``:
            - Contains list of all attributes from various fields in form of list of name-value dict.
            - Useful for analytics and querying since it has indexes.
            - This field must not be changed directly as it will be overridden during save.
            - Fields that populate this field are: ``attributes``
        - The ``address`` field can be None in case of some BSP such as doctor who works at a clinic.
        - If ``active`` is false, BSP is as good as deleted. This will not show up anywhere other than owners account.
          A BSP can be reverted back to active by setting this as true.

    **Authors**: Gagandeep Singh
    """

    # --- Embedded documents ---
    class ImageDoc(EmbeddedDocument):
        """
        Mongodb embedded document to store photo urls for a BSP.

        **Authors**: Gagandeep Singh
        """
        url     = URLField(required=True, help_text='Absolute url of the image where the image is stored.')
        title   = StringField(help_text="Title of the image.")
        description = StringField(help_text='Any description regarding this image.')

    class Attribute(EmbeddedDocument):
        """
        Mongodb embedded document to store BSP attribute.

        **Authors**: Gagandeep Singh
        """
        name    = StringField(required=True, help_text='Name of the attribute.')
        value   = BaseField(required=True, help_text='Value of the attribute.')

        def __unicode__(self):
            return self.name


    class DayTiming(EmbeddedDocument):
        """
        Mongodb embedded document to store a week day timings.
        """
        SUN = 'Sun'
        MON = 'Mon'
        TUE = 'Tue'
        WED = 'Wed'
        THU = 'Thu'
        FRI = 'Fri'
        SAT = 'Sat'
        CH_DAY = (
            (SUN, SUN),
            (MON, MON),
            (TUE, TUE),
            (WED, WED),
            (THU, THU),
            (FRI, FRI),
            (SAT, SAT)
        )

        day = StringField(required=True, choices=CH_DAY, help_text="Day of the week in three letters as per datetime '%a'.")
        start_time = IntField(help_text='Start time in 24-hour format as HHMM. Example: 0930 (9:30 AM)')
        end_time = IntField(help_text='End time in 24-hour format as HHMM. Example: 1800 (6 PM)')
        closed  = BooleanField(default=None, help_text='If true, it means BSP is closed on that day.')
        full_day = BooleanField(default=None, help_text='If true, it means open for 24-hours. This will update start-end to 0000-2400')

        def __init__(self, *args, **kwargs):
            if not self.closed:
                if self.start_time is None or self.end_time:
                    raise ValidationError("Please enter start time & end time for the day timing.")

            if self.full_day:
                self.start_time = 0000
                self.end_time = 2400

            super(BusinessServicePoint.DayTiming, self).__init__(*args, **kwargs)


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
        (ST_OPN_CLOSED, 'Closed')
    )

    # --- Fields ---
    bsp_uid     = StringField(required=True, unique=True, help_text="Unique id of the BSP. This will be shared with public.")
    name        = StringField(required=True, help_text="Name of the business or service point. Thius can be duplicates.")
    description = StringField(help_text='Description about this BSP.')

    # TODO: type, organsiation, brand, members
    # type        = models
    # organisation    =
    # brand         =
    # members

    # Attributes
    attributes  = DictField(required=True, help_text='Attributes of BSP according to BspType. Use this for reporting or display.')
    timings     = EmbeddedDocumentListField(DayTiming, help_text='Week day wise timings. This can hav multiple timings for a day.')

    list_attributes = EmbeddedDocumentListField(Attribute, required=True, help_text="List of all attributes from various fields. These are populated by 'attributes' so do not update here. Use this for analytics.")

    # Media
    cover_photo = EmbeddedDocumentField(ImageDoc, help_text='Cover photo of this BSP.')
    photos      = EmbeddedDocumentListField(ImageDoc, help_text='Multiple images for this BSP.')


    # Contact
    contacts    = EmbeddedDocumentListField(ContactEmbDoc, help_text="Contact number list for this BSP.")
    address     = EmbeddedDocumentField(AddressEmbDoc, help_text="Address of this BSP.")
    emails      = ListField(help_text='Email ids')
    website     = URLField(help_text='Website url if any.')

    # Stats
    avg_rating  = FloatField(default=None, help_text="Average rating.")
    total_views = IntField(default=0, help_text="Total views for this bsp.")

    # Misc
    tags        = ListField(help_text='Tags related to this BSP.')
    social      = EmbeddedDocumentField(SocialMedia, help_text='Social media page links.')
    other_details = StringField(help_text='Any other details regarding this BSP.')

    # Statuses
    verification_status = StringField(required=True, help_text='Verification status of the BSP.')
    open_status = StringField(required=True, default=ST_OPN_OPEN, choices=CH_OPEN_STATUS, help_text='Open status of BSP.')
    active      = BooleanField(default=True, required=True, help_text='Set false, to temporarily deactive/hide this bsp.')

    created_by  = IntField(required=True, help_text="Instance id of user :class:`django.contrib.auth.models.User` who created this BSP. This is not RegisteredUser.")

    # Dates
    created_on  = DateTimeField(default=timezone.now, required=True, help_text='Date on which this record was created in the database.')
    modified_on = DateTimeField(default=None, help_text='Date on which this record was modified.')

    meta = {
        'indexes':[
            'bsp_uid',
            '$name',

            ('list_attributes.name', 'list_attributes.value'),
            { 'fields':['timings.day', 'timings.start_time', 'timings.end_time'], 'cls':False, 'sparse': True },
            { 'fields':['timings.day', 'timings.closed'], 'cls':False, 'sparse': True },

            { 'fields':['address.coordinates'], 'cls':False, 'sparse': True },
            { 'fields':['address.location_id'], 'cls':False, 'sparse': True },

            { 'fields':['avg_rating'], 'cls':False, 'sparse': True },
            { 'fields':['tags'], 'cls':False, 'sparse': True },

            'verification_status',
            'open_status',
            'active',

            'created_by',
            'created_on'
        ]
    }

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """
        if self.pk is None:
            # TODO: Create bsp_uid
            pass

        if self.pk:
            self.modified_on = timezone.now()

        # --- Validate timings ---
        list_timings = []
        for day_tmng in self.timings:
            if day_tmng.closed:
                day_tmng.start_time = None
                day_tmng.end_time = None

            if day_tmng.full_day:
                self.start_time = 0000
                self.end_time = 2400

            list_timings.append(day_tmng)
        self.timings = list_timings

        if update_attr:
            list_attr = []
            for key, val in self.attributes.iteritems():
                if not isinstance(val, dict):
                    list_attr.append(
                        BusinessServicePoint.Attribute(
                            name = key,
                            value = val
                        )
                    )
            self.list_attributes = list_attr

        return super(BusinessServicePoint, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        raise ValidationError("You cannot delete a BSP. Instead mark 'active' as false.")