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
    HELP_TEXT = {
        "street_address": "Flat/Block/Street address",
        "landmark": "Landmark near the address.",
        "locality": "Locality",
        "city": "City/Town/Village",
        "state": "State",
        "country": "Country",
        "pincode": "Pincode or Postal code",
        "coordinates": "GPS location in order of longitude and latitude separated by comma e.g. <lng>,<lat>"
    }

    location_code = StringField(required=True, confidential=True, help_text='Code of :class:`geography.models.GeoLocation`.')

    street_address = StringField(required=True, help_text="Street address that mostly includes house/flat number.")
    landmark    = StringField(help_text='Landmarks for this address.')

    locality    = StringField(help_text="As per location model instance.")
    city        = StringField(help_text="As per location model instance.")
    state       = StringField(help_text="As per location model instance.")
    country     = StringField(help_text="As per location model instance.")
    pincode     = StringField(help_text="As per location model instance.")

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

    HELP_TEXT = {
        "type": 'Type of contact number.<br/>Values: ' + ', '.join(['<code>{}</code>'.format(t[0]) for t in CH_TYPE]),
        "tel_code": "Telephone code/prefix",
        "number": "Contact number"
    }

    type    = StringField(required=True, choices=CH_TYPE, help_text='Type of contact number; mobile/landline/fax etc.')
    tel_code = StringField(required=True, help_text='Telephone code/prefix.')
    number  = IntField(required=True, help_text='Contact number.')

    def __unicode__(self):
        return "{}".format(self.number)

