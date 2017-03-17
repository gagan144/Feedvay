# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

from mongoengine.document import *
from mongoengine.fields import *

'''
class AdministrativeDivision:
    """
    Static class to define administrative division. It essentially defines hierarchies between various levels of the division.
    Each levels is associated with integer value with lowest being higher level.

    **Authors**: Gagandeep Singh
    """

    # --- Enums ---
    LVL_COUNTRY = 'country'
    LVL_STATE   = 'state'
    LVL_CITY    = 'city'
    LVL_TOWN    = 'town'
    LVL_VILLAGE = 'village'
    LVL_LOCALITY = 'locality'

    CH_LEVELS = (
        (LVL_COUNTRY, 'Country'),
        (LVL_STATE, 'State'),
        (LVL_CITY, 'City'),
        (LVL_TOWN, 'Town'),
        (LVL_VILLAGE, 'Village'),
        (LVL_LOCALITY, 'Locality')
    )

    # --- Hierarchies ---
    HIER_ST_CTY_LCLTY = 'state_city_locality'

    CH_TREES = (
        (HIER_ST_CTY_LCLTY, 'State-City-Locality'),
    )

    HIERARCHIES = {
        HIER_ST_CTY_LCLTY: {
            LVL_COUNTRY: 0,
            LVL_STATE: 1,

            LVL_CITY: 2,
            LVL_TOWN: 2,
            LVL_VILLAGE: 2,

            LVL_LOCALITY: 3
        }
    }

'''

class GeoDataSource(Document):
    """
    Collection to store referneces to various data sources used for creating
    geographical database.

    **Authors**: Gagandeep Singh
    """
    codename    = StringField(required=True, unique=True, help_text='Unique codename for this data source.')
    name        = StringField(required=True, help_text='Name of the data source.')
    reference   = StringField(required=True, help_text='Book/URL/White paper etc reference.')

    # meta = {
    #     'indexes':[
    #         'codename'
    #     ]
    # }

    def __unicode__(self):
        return self.name

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete a geo data source record.")


class GeoLocation(Document):
    """
    MongoDb collection that stores location or terrain or to be precise administrative division such as a
    Country, State, City, Town, Village, Locality, District etc.

    **Schema Design**:

        - Each entity/row/document in this collection defines a location or a terrain of some administrative division type (Country/State/City etc).
        - Each location can be associated or can be a part of one or more administrative division hierarchy. These are maintained in
          embedded list document that specifies hierarchy codename, level of this location in the hierarchy and path.
        - Location may have a post office. If so details are maintained in embedded field ``post_office`` with pincode etc. This is usually
          applicable for location of type ``locality``.
        - Location may have some geographical details such as centroid GPS location or a geographical shape.

    **Uniqueness**:

        - ``name``, ``division_type`` : Name cannot be duplicate for same division type.
        - ``code_iso`` : ISO 3166 codes must be unique for non null values
        - ``pk``, ``hierarchies.hierarchy``, ``hierarchies.level_id`` : Location cannot be at various level under a hierarchy.

    .. warning::
        This collection is **STATIC** and is not subjected to often changes since most of the data has already been verified.
        Please be careful while updating data as this ORM does not provide any triggers or validations to check consistency.
        Careless amendments can result into unusual behavior. Please read the document carefully.

        **DO NOT** use mongo generated id to refer location. Use ``code`` instead.

    **Authors**: Gagandeep Singh
    """

    # --- Embedded classes ---
    class AdministrativeHierarchy(EmbeddedDocument):
        """
        Mongo embedded document to define location node in administrative division hierarchy.

        **Authors**: Gagandeep Singh
        """
        hierarchy   = StringField(required=True, help_text='Codename of the administrative division hierarchy.')
        level_id    = IntField(required=True, help_text='Integer value representing level in the hierarchy.')
        path        = StringField(required=True, help_text="'+' (Plus) separated path in the hierarchy.")

        statistics  = DictField(help_text='Statistics or information relate to the location in this hierarchy.')

        def __unicode__(self):
            return "{}".format(self.path)

    class PostOffice(EmbeddedDocument):
        """
        Mongo embedded document for post office.

        **Authors**: Gagandeep Singh
        """
        pincode     = StringField(required=True, help_text='Pincode/Postcode of the post office')
        office_name = StringField(help_text="Name of the office.")
        office_type = StringField(help_text='Type of post office.')
        telephone   = StringField(help_text='Any telephone number of the office.')

        def __unicode__(self):
            return "{}".format(self.pincode)

    # --- Fields ---
    name        = StringField(required=True, help_text='Name of the location (May be duplicate).')
    division_type = StringField(required=True, unique_with='name', help_text='Administrative division type in terms of Country/State/City/Town/Village etc.')

    # codes
    code_iso    = StringField(required=False, sparse=True, unique=True, help_text='Code as per ISO 3166. (ISO 3166-1: For country, ISO 3166-2: For country subdivisions)')
    code        = StringField(required=True, unique=True, help_text="Unique code for this location. Can be equal to ``code_iso``.")

    hierarchies = EmbeddedDocumentListField(AdministrativeHierarchy, help_text="Administrative division hierarchies for this location.")

    # Pincode/Postal office information
    post_office = EmbeddedDocumentField(PostOffice, help_text="Post office information if any. Mostly in case of 'locality' level.")

    # Geographical details
    centroid    = GeoPointField(help_text='Centroid GPS coordinates of this location.')
    shape       = PolygonField(help_text='Shape of this location.')

    # Misc
    data_sources = ListField(required=True, help_text='List of sources from where the data was compiled. These are raw codename reference to :class:`geography.models.GeoDataSource`.')
    dated       = DateTimeField(required=True, help_text='Date on which this data was generated.')
    modified_on = DateTimeField(help_text="Date on which data for this terrain was last modified.")

    meta = {
        'indexes':[
            '$name',
            ('name', 'division_type'),
            { 'fields': ['code_iso'], 'cls':False, 'sparse': True },
            'code',
            { 'fields': ['pk', 'hierarchies.hierarchy', 'hierarchies.level_id'], 'cls':False, 'sparse': True },
            { 'fields': ['post_office.pincode'], 'cls':False, 'sparse': True },
            { 'fields': ['centroid'], 'cls':False, 'sparse': True },
            { 'fields': ['shape'], 'cls':False, 'sparse': True },
            'data_sources'
        ]
    }

    def __unicode__(self):
        return "{} ({})".format(self.name, self.division_type)

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete a location record.")
