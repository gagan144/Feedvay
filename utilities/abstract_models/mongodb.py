# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField

class AddressEmbDoc(EmbeddedDocument):
    """
    Mongodb embedded document to store address.

    **Authors**: Gagandeep Singh
    """
    location_id = StringField(required=True, help_text='Instance id of Location model.')

    street_address = StringField(required=True, help_text="Street address that mostly includes house/flat number.")
    landmark    = StringField(help_text='Landmarks for this address.')

    locality    = StringField(required=True, help_text="As per location model instance.")
    city        = StringField(required=True, help_text="As per location model instance.")
    state       = StringField(required=True, help_text="As per location model instance.")
    country     = StringField(required=True, help_text="As per location model instance.")
    pincode     = IntField(min_value=100000, max_value=999999, help_text="As per location model instance.")

    coordinates = GeoPointField(sparse=True)


    def __unicode__(self):
        return "{}, {}".format(self.street_address, self.locality)

class ContactEmbDoc(EmbeddedDocument):
    """
    Mongodb embedded document to store phone/mobile numbers.

    **Authors**: Gagandeep Singh
    """
    MOBILE = 'mobile'
    LANDLINE = 'landline'
    FAX = 'fax'
    CH_TYPE = (
        (MOBILE, 'Mobile'),
        (LANDLINE, 'Landline'),
        (FAX, 'Fax')
    )

    type    = StringField(required=True, choices=CH_TYPE, help_text='Type of contact number; mobile/landline/fax etc.')
    code    = StringField(required=True, help_text='Telephone code/prefix.')
    number  = IntField(required=True, help_text='Contact number.')

    def __unicode__(self):
        return "{}".format(self.number)

