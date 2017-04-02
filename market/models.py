# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.db.models.fields.files import ImageFieldFile
from django_mysql import models as models57
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
import uuid, os, shortuuid, StringIO
import tinymce.models as tinymce_models
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django.core.files.uploadedfile import InMemoryUploadedFile,SimpleUploadedFile
from PIL import Image
from jsonobject import *
from jsonobject.exceptions import *
from operator import itemgetter

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField, ObjectId

from django.contrib.auth.models import User

from accounts.models import RegisteredUser
from clients.models import Organization
from utilities.theme import UiTheme, ColorUtils, render_skin
from utilities.abstract_models.mongodb import AddressEmbDoc, ContactEmbDoc
from market.bsp_types import *
from form_builder.validators import validate_label
from utilities.db_mongo import MAPPING_MONGO_FLD_PYTHON
from utilities.jsonobject_utils import MAPPING_JSNOBJ_FLD_PYTHON

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

# ========== Brand ==========
def upload_brand_logo_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/brands/{brand_uid}/lg-{filename}".format(
        org_uid = str(instance.organization.org_uid),
        brand_uid = str(instance.brand_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_brand_icon_to(instance, filename):
    id = str(uuid.uuid4())
    fname, ext = os.path.splitext(filename)
    new_filename = "{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/brands/{brand_uid}/ic-{filename}".format(
        org_uid = str(instance.organization.org_uid),
        brand_uid = str(instance.brand_uid),
        filename = new_filename #filename.replace(" ","_")
    )
def upload_brand_theme_file_to(instance, filename):
    id = str(shortuuid.ShortUUID().random(length=10))
    fname, ext = os.path.splitext(filename)
    new_filename = "theme_{}.{}".format(id, ext.replace('.',''))

    return "organizations/{org_uid}/brands/{brand_uid}/{filename}".format(
        org_uid = str(instance.organization.org_uid),
        brand_uid = str(instance.brand_uid),
        filename = new_filename #filename.replace(" ","_")
    )
class Brand(models57.Model):
    """
    Model to store brand of an organization. A brand is any name, design, style, words or symbols used
    singularly or in combination that distinguish one product from another in the eyes of the customer.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    LOGO_DIM = (300, 100)
    LOGO_MAX_SIZE = 30*1024 # in bytes

    ICON_DIM = (64, 64)
    ICON_MAX_SIZE = 15*1024 # in bytes

    # --- Fields ---
    organization = models.ForeignKey(Organization, db_index=True, help_text='Organization to which this brand belongs to.')
    brand_uid   = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, help_text='Unique ID of a brand which are hard to guess and can be used in urls. ')
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text='Name of the brand.')
    slug        = models.SlugField(unique=True, blank=True, db_index=True, help_text='Slug of the name used for url referencing and dedupe matching.')

    # Settings
    description = models.TextField(help_text='Short description about the brand.')
    logo        = models.ImageField(max_length=512, upload_to=upload_brand_logo_to, help_text='Brand logo of size 300x100 pixels.')
    icon        = models.ImageField(max_length=512, upload_to=upload_brand_icon_to, help_text='Brand icon of size 64x64 px.')

    # Customization
    ui_theme    = models57.JSONField(default=None, blank=True, null=True, help_text="Custom UI theme for this brand. This must be of format 'utilities.theme.UiTheme'")
    theme_file  = models.FileField(max_length=256, upload_to=upload_brand_theme_file_to, editable=False, help_text='Theme file link which is automatically generated if ui_theme is defined')

    # Status
    active      = models.BooleanField(default=True, db_index=True, help_text='If false, it means brand is currenlty inactive.')

    # Misc
    created_by  = models.ForeignKey(User, editable=False, related_name='created_by', help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('name', )
        permissions = (
            ("view_brand", "Can view brands"),
        )

    def __unicode__(self):
        return "{} ({})".format(self.name, self.organization.name)


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
        raise ValidationError("You cannot delete a brand. Mark 'active' false instead.")

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

# ========== /Brand ==========


# ========== Business or Service Point ==========
def validate_unique_label(schema):
    list_found = []
    for attr in schema:
        label = attr['label']
        if list_found.__contains__(label):
            raise ValidationError("Duplicate label '{}' in attributes.".format(label))
        else:
            list_found.append(label)

class BspTypeCustomization(models57.Model):
    """
    Model to customize a BSP type in terms of attributes for an organization.
    All BSPs have certain common attributes as well as attributes related to their type.
    However, it is possible that organization might want certain more attributes other than
    provided ones for their own use.

    This model allows organizations to define attributes and their data type.

    **Points**:

        - Only one customization can be defined for organization-BSP basis.
        - Data types for attributes are limited.

    **Authors**: Gagandeep Singh
    """
    # --- Classes ---
    class Attribute(JsonObject):
        """
        Attribute schema to define a custom bsp attribute.

        **Authors**: Gagandeep Singh
        """
        class ENUMS:
            DTYPE_INT = 'int'
            DTYPE_FLOAT = 'float'
            DTYPE_TEXT = 'text'
            DTYPE_BOOL = 'bool'
            CH_DTYPES = (
                (DTYPE_INT, 'Number'),
                (DTYPE_FLOAT, 'Decimal'),
                (DTYPE_TEXT, 'Text'),
                (DTYPE_BOOL, 'Boolean'),
            )

        _allow_dynamic_properties = False

        label   = StringProperty(required=True, validators=[validate_label]) # Lowercase label of the attribute. This is what value is stored against. Follow variable conventions.
        name    = StringProperty(required=True)    # Name of the attribute. Free text.
        dtype   = StringProperty(required=True, choices=ENUMS.CH_DTYPES)   # Data-type of the attribute

        # def __init__(self, _obj=None, **kwargs):
        #     super(BspTypeCustomization.Attribute, self).__init__(_obj=_obj, **kwargs)



    # --- Fields ---
    organization = models.ForeignKey(Organization, help_text='Organization for which this customization is defined.')
    bsp_type    = models.CharField(max_length=64, choices=BspTypes.choices, help_text='BSP that is customized.')

    schema      = models57.JSONField(validators=[validate_unique_label], help_text='Schema (list of objects) that defines custom attributes.')

    created_by  = models.ForeignKey(User, editable=False, help_text='Person who created this customization.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        unique_together = ('organization', 'bsp_type')
        permissions = (
            ('view_bsptypecustomization', 'Can be bsp type customizations'),
        )

    def __unicode__(self):
        return "{} - {}".format(self.bsp_type, self.organization.name)

    def get_attribute_schema(self, label):
        """
        Method to get attribute schema :class:`market.models.BspTypeCustomization.Attribute` given
        a label key.

        :param label: Label of the attribute to be searched
        :return: :class:`market.models.BspTypeCustomization.Attribute` instance or None if not found
        """
        for attr_dict in self.schema:
            if attr_dict['label'] == label:
                return BspTypeCustomization.Attribute(attr_dict)

        return None

    def get_attribute_labels_list(self):
        """
        Method to return all list of attribute labels.

        :return: List
        """
        list_labels = [attr['label'] for attr in self.schema]
        return list_labels

    def validate_data(self, data_dict):
        """
        Method to validate data dict as per the schema.

        :param data_dict: Dict if key-value data
        :return: (is_valid, error_msg) True if valid else False with error message
        """
        is_valid = True
        error_msg = None

        list_labels = self.get_attribute_labels_list()
        for label, value in data_dict.iteritems():
            if label not in list_labels:
                is_valid = False
                error_msg = "Invalid custom attribute '{}'. Allowed are {}.".format(label, ','.join(list_labels))

        return (is_valid, error_msg)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        # Validate schema
        if isinstance(self.schema, list):
            for attr in self.schema:
                try:
                    a_obj = BspTypeCustomization.Attribute(attr)
                except (BadValueError, WrappingAttributeError) as ex:
                    raise ValidationError("Schema error: {}".format(ex.message))
        else:
            raise ValidationError('Schema must be a list.')

        # Check for reserved labels
        list_reserved_labels = BusinessServicePoint._fields.keys() + MAPPING_BSP_CLASS[self.bsp_type].properties().keys()
        for attr in self.schema:
            attr['label'] = attr['label'].lower()   # Convert labels to lowercase

            if attr['label'] in list_reserved_labels:
                raise ValidationError("Label '{}' is reserved.".format(attr['label']))

        if self.pk:
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


# --- BSP related models ---
class RestaurantCuisine(models.Model):
    """
    Model to store various types of restaurant cuisines.

    **Authors**: Gagandeep Singh
    """
    name    = models.CharField(max_length=64, unique=True, db_index=True, help_text='Name/title of the cuisines.')
    active  = models.BooleanField(default=True, db_index=True, help_text='If false, this will not be visible. Deactivating will not affect currently associated restaurants.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('name', )

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

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete a restaurant cuisines. Instead mark 'active' as false.")
# --- /BSP related models ---

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

    ..warning::
        If you want to add any new field to this table, do not forget to make entry in ``HELP_TEXT`` for
        non confidential fields.

    **Authors**: Gagandeep Singh
    """

    # --- Embedded documents ---
    class ImageDoc(EmbeddedDocument):
        """
        Mongodb embedded document to store photo urls for a BSP.

        **Authors**: Gagandeep Singh
        """
        HELP_TEXT = {
            "url": "URL of the photo.",
            "title": "Title for the photo.",
            "description": "Some description about the photo."
        }


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

        HELP_TEXT = {
            "day": "Three letter day of the week.",
            "start_time": "Start time in 24-hour format as HHMM. Example: 0930 (9:30 AM)",
            "end_time": "End time in 24-hour format as HHMM. Example: 1800 (6 PM)",
            "closed": "Whether BSP is closed on the duration for the day.",
            "full_day": "Whether the BSP is opened for 24-hours for the day."
        }

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
        HELP_TEXT = {
            "facebook": "Link to facebook page.",
            "twitter": "Link to twitter page."
        }

        facebook    = URLField(help_text='Link to facebook page.')
        twitter     = URLField(help_text='Link to twitter page.')


    class FeedbackFormEmbd(EmbeddedDocument):
        """
        Mongodb embedded document to store attached BSP feedback form as well as its
        change history.

        **Authors**: Gagandeep Singh
        """

        class ChangeHistory(EmbeddedDocument):
            """
            Mongodb embedded document to store BSP feedback form change history.

            **Authors**: Gagandeep Singh
            """
            form_id     = IntField(help_text="Instance ID of :class:`feedback.models.BspFeedbackForm` which is currently attached.")
            associated_by_id = IntField(help_text='Instance ID of User who associated this form.')
            dated       = DateTimeField(help_text="Date on which the form was attached.")

            @property
            def form(self):
                from feedback.models import BspFeedbackForm
                return BspFeedbackForm.objects.get(id=self.form_id)

            @property
            def associated_by(self):
                return User.objects.get(id=self.associated_by_id)

            def __unicode__(self):
                return "{}".format(self.form_id)

        form_id     = IntField(help_text="Instance ID of :class:`feedback.models.BspFeedbackForm` which is currently attached.")
        associated_by_id = IntField(help_text='Instance ID of User who associated this form.')
        ai_comment_directives = DictField(help_text='AI directives (:class:`form_builder.fields.AiTextDirectives`) specifying AI to be applied on feedback comments.')
        dated       = DateTimeField(help_text="Date on which the form was attached.")
        change_history = EmbeddedDocumentListField(ChangeHistory, help_text="Feedback form change history. This also includes currently attached form.")

        @property
        def form(self):
            if self.form_id:
                from feedback.models import BspFeedbackForm
                return BspFeedbackForm.objects.get(id=self.form_id)
            else:
                return None

        @property
        def associated_by(self):
            return User.objects.get(id=self.associated_by_id)

        def __unicode__(self):
            return "{}".format(self.form_id)

    # --- Enums ---
    ST_OPN_OPEN = 'open'
    ST_OPN_COMING_SOON = 'coming_soon'
    ST_OPN_CLOSED = 'closed'
    # ST_OPN_REMOVED = 'removed'
    CH_OPEN_STATUS = (
        (ST_OPN_OPEN, 'Open'),
        (ST_OPN_COMING_SOON, 'Coming Soon'),
        (ST_OPN_CLOSED, 'Closed')
    )

    # Help text for users understanding for non confidential fields only.
    # Please keep this updated and use simple-understandable explanations.
    HELP_TEXT = {
        "name": "Name of your business or service point.",
        "description": "Description about your business or service point.",

        "type": "Type of business or service point.",
        "brand_id": "The brand to which the BSP belongs to.",

        "timings": "Weekday wise opening or closing timings for the BSP if any.",

        "cover_photo": "Cover photo for the BSP.",
        "photos": "Photos for the BSP.",

        "contacts": "List of phone contacts.",
        "address": "Address of the BSP (if any).",
        "emails": "List of email address for the BSP (if any).",
        "website": "Your website/URL to view the BSP for example https://www.mywebsite.com/some-path/",

        "tags": "Tag BSP with words, keywords etc.",
        "social": "Social media site references such as facebook, twitter etc.",
        "other_details": "Any other details for regarding the BSP."
    }


    # --- Fields ---
    # bsp_uid     = StringField(required=True, unique=True, confidential=True, help_text="Unique Feedvay id of the BSP. This will be shared with public.")
    name        = StringField(required=True, help_text="Name of the business or service point. This can be duplicates.")
    description = StringField(help_text='Description about this BSP.')

    type        = StringField(required=True, choices=BspTypes.choices, avoid=True, help_text="Type of BSP.")
    organization_id = IntField(required=True, confidential=True, help_text="Instance id of the organization to which this BSP belongs to.")
    brand_id    = IntField(help_text="(Optional) Instance id of the brand to which this BSP belongs to.")

    # Attributes
    attributes  = DictField(required=True, confidential=True, help_text='Pre-defined attributes of BSP according to BspType. Use this for reporting or display.')
    custom_attributes = DictField(confidential=True, help_text='Any other custom attributes. These are free to be updated.')
    timings     = EmbeddedDocumentListField(DayTiming, avoid=True, help_text='Week day wise timings. This can have multiple timings for a day.')

    list_attributes = EmbeddedDocumentListField(Attribute, required=True, confidential=True, help_text="List of all attributes from various fields. These are populated by 'attributes' so do not update here. Use this for analytics.")

    # Media
    cover_photo = EmbeddedDocumentField(ImageDoc, avoid=True, help_text='Cover photo of this BSP.')
    photos      = EmbeddedDocumentListField(ImageDoc, avoid=True, help_text='Multiple images for this BSP.')


    # Contact
    contacts    = EmbeddedDocumentListField(ContactEmbDoc, avoid=True, help_text="Contact number list for this BSP.")
    address     = EmbeddedDocumentField(AddressEmbDoc, avoid=True, help_text="Address of this BSP.")
    emails      = ListField(help_text='Email ids')
    website     = URLField(help_text='Website url if any.')

    # Stats
    avg_rating  = FloatField(default=0, confidential=True, help_text="Average rating.")
    total_views = IntField(default=0, confidential=True, help_text="Total views for this bsp.")

    # Misc
    tags        = ListField(help_text='Tags related to this BSP.')
    social      = EmbeddedDocumentField(SocialMedia, avoid=True, help_text='Social media page links.')
    other_details = StringField(help_text='Any other details regarding this BSP.')

    # feedback_form_id = IntField(help_text="Feedback form attached to this BSP. Instance ID of :class:`feedback.models.BspFeedbackForm`.")
    feedback_form = EmbeddedDocumentField(FeedbackFormEmbd, help_text="Fedeback form attached to it.")

    # Statuses
    # verification_status = StringField(required=True, confidential=True, help_text='Verification status of the BSP.')
    open_status = StringField(required=True, confidential=True, default=ST_OPN_OPEN, choices=CH_OPEN_STATUS, help_text='Open status of BSP.')
    active      = BooleanField(default=True, confidential=True, required=True, help_text='Set false, to temporarily deactive/hide this bsp.')

    created_by  = IntField(required=True, confidential=True, help_text="Instance id of user :class:`django.contrib.auth.models.User` who created this BSP. This is not RegisteredUser.")

    # Dates
    created_on  = DateTimeField(default=timezone.now, required=True, confidential=True, help_text='Date on which this record was created in the database.')
    modified_on = DateTimeField(default=None, confidential=True, help_text='Date on which this record was modified.')

    @property
    def organization(self):
        return Organization.objects.get(id=self.organization_id)

    @property
    def brand(self):
        return Brand.objects.get(id=self.brand_id)

    @property
    def created_by_user(self):
        return User.objects.get(id=self.created_by) if self.created_by else None

    # @property
    # def feedback_form(self):
    #     if self.feedback_form_id:
    #         from feedback.models import BspFeedbackForm
    #         return BspFeedbackForm.objects.get(id=self.feedback_form_id)
    #     else:
    #         return None

    meta = {
        'indexes':[
            # 'bsp_uid',
            '$name',
            'type',
            'organization_id',
            { 'fields':['brand_id'], 'cls':False, 'sparse': True },

            ('list_attributes.name', 'list_attributes.value'),
            { 'fields':['timings.day', 'timings.start_time', 'timings.end_time'], 'cls':False, 'sparse': True },
            { 'fields':['timings.day', 'timings.closed'], 'cls':False, 'sparse': True },

            { 'fields':['address.coordinates'], 'cls':False, 'sparse': True },
            { 'fields':['address.location_code'], 'cls':False, 'sparse': True },

            { 'fields':['avg_rating'], 'cls':False, 'sparse': True },
            { 'fields':['tags'], 'cls':False, 'sparse': True },

            # { 'fields':['feedback_form_id'], 'cls':False, 'sparse': True },
            { 'fields':['feedback_form.form_id'], 'cls':False, 'sparse': True },

            # 'verification_status',
            'open_status',
            'active',

            'created_by',
            'created_on'
        ],
        'ordering': ['name']
    }

    def __unicode__(self):
        return "{}".format(self.name)

    # --- Feedback form methods ---
    def associate_feedback_form(self, form, ai_directives, user):
        """
        Method to associate BspFeedbackForm to this BSP.

        :param form: Instance of :class:`feedback.models.BspFeedbackForm` that is to be attached.
        :param ai_directives: Instance of :class:`form_builder.fields.AiTextDirectives` for comments. If 'None' settings are not changed.
        :param user: Instance of :class:`django.contrib.auth.models.User` who attached this form.

        **Authors**: Gagandeep Singh
        """
        from feedback.models import BspFeedbackForm
        if not isinstance(form, BspFeedbackForm):
            raise ValidationError("'form' is not an instance of BspFeedbackForm.")

        now = timezone.now()
        embd_feedback_form = self.feedback_form
        if embd_feedback_form is None:
            embd_feedback_form = BusinessServicePoint.FeedbackFormEmbd()

        embd_feedback_form.form_id = form.id
        embd_feedback_form.associated_by_id = user.id
        if ai_directives is not None:
            embd_feedback_form.ai_comment_directives = ai_directives.to_json()

        embd_feedback_form.dated = now
        embd_feedback_form.change_history.append(
            BusinessServicePoint.FeedbackFormEmbd.ChangeHistory(
                form_id = form.id,
                associated_by_id = user.id,
                dated = now,
            )
        )

        self.feedback_form = embd_feedback_form
        self.save()

    def deassociate_feedback_form(self, confirm=False):
        """
        Method to de-associate currently attached feedback form. This will
        ignore if frm is already detached.

        :return: True if action was taken else False

        **Authors**: Gagandeep Singh
        """
        if not confirm:
            raise ValidationError("Please confirm your action.")

        if self.feedback_form and self.feedback_form.form_id:
            self.feedback_form.form_id = None
            self.feedback_form.associated_by_id = None
            self.feedback_form.dated = None

            self.save()
            return True

        return False

    # --- /Feedback form methods ---

    def to_js_json(self, include_list_attr=False, include_feedback=False):
        """
        Method to convert model object to javascript JSON in equivalent python dict.

        :param include_list_attr: If True, ``list_attributes`` is included.
        :return: JSON

        **Authors**: Gagandeep Singh
        """
        data = self.to_mongo().to_dict()

        if not include_list_attr:
            del data['list_attributes']
        if not include_feedback:
            if data.has_key('feedback_form'):
                del data['feedback_form']

        # Convert python types to js equivalent
        for key, val in data.iteritems():
            if isinstance(val, datetime):
                data[key] = val.strftime("%Y-%m-%dT%H:%M:%S")
            elif isinstance(val, ObjectId):
                data[key] = str(val)

        return data

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """
        if self.pk is None:
            # Create bsp_uid
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

            for key, val in self.custom_attributes.iteritems():
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
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete a BSP. Instead mark 'active' as false.")


# ---------- Global methods ----------
def get_bsp_labels(bsp_type_code, org=None):
    """
    Method to get all labels and its information for a bsp type.

    :param bsp_type_code: Codename of the BSP type.
    :param org: (Optional) If provided, it also includes custom attributes created by an organization for that BSP.
    :return: List of dict objects.

    **Return list structure**:

        .. code-block:: json

            [
                {
                    "label": "<Field label>",
                    "description": "<Description of the field>",
                    "dtype": "<Data ype of the field>",
                    "required": true,
                    "path": "<Dot separated path in the model>",
                    "is_common": "<true/false: If true means this attribute is common across all BSP>"
                },

            ]

    **Authors**: Gagandeep Singh
    """
    data = []

    # (a) Common attributes
    map_fields = BusinessServicePoint._fields
    list_fields = ((v.creation_counter, k) for k,v in BusinessServicePoint._fields.iteritems())
    sorted_list_fields = map(itemgetter(1), sorted(list_fields, key=itemgetter(0)))

    # for lbl, fld in BusinessServicePoint._fields.iteritems():
    for lbl in sorted_list_fields:
        fld = map_fields[lbl]
        if lbl != 'id' and getattr(fld, 'confidential', getattr(fld, 'avoid', False) ) == False:
            data.append({
                "label": lbl,
                "description": BusinessServicePoint.HELP_TEXT[lbl],
                "dtype": MAPPING_MONGO_FLD_PYTHON[fld.__class__.__name__].__name__,
                "required": fld.required,
                "path": lbl,
                "is_common": True
            })

        # contacts, address, social
        if lbl in ['contacts', 'address', 'social']:
            if isinstance(fld, EmbeddedDocumentListField):
                embd_doc = fld.field.document_type
            else:
                embd_doc = fld.document_type

            for sub_lbl, sub_fld in embd_doc._fields.iteritems():
                if getattr(sub_fld, 'confidential', False) == False:
                    data.append({
                        "label": sub_lbl,
                        "description": embd_doc.HELP_TEXT[sub_lbl],
                        "dtype": MAPPING_MONGO_FLD_PYTHON[sub_fld.__class__.__name__].__name__,
                        "required": sub_fld.required,
                        "path": "{}.{}".format(lbl, sub_lbl),
                        "is_common": True
                    })

    # (b) BSP type related attributes
    type_class = MAPPING_BSP_CLASS[bsp_type_code]
    for lbl, fld in type_class.properties().iteritems():
        data.append({
            "label": lbl,
            "description": type_class.ENUMS.HELP_TEXT[lbl],
            "dtype": MAPPING_JSNOBJ_FLD_PYTHON[fld.__class__.__name__].__name__,
            "required": fld.required,
            "path": "attributes.{}".format(lbl),
            "is_common": False
        })

    # (c) Custom attributes as per the organization
    if org:
        try:
            cust_attr = BspTypeCustomization.objects.get(organization=org, bsp_type=bsp_type_code)

            for attr in cust_attr.schema:
                data.append({
                    "label": attr['label'],
                    "description": attr['name'],
                    "dtype": attr['dtype'],
                    "required": False,
                    "path": "custom_attributes.{}".format(attr['label']),
                    "is_common": False
                })
        except BspTypeCustomization.DoesNotExist:
            pass

    return data