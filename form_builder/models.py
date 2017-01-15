# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import tinymce.models as tinymce_models
from django_mysql import models as models57
from django_extensions.db.fields.json import JSONField
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from colorful.fields import RGBColorField
from django.db.models.signals import post_save

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.base.fields import BaseField

from django.core.exceptions import ValidationError
import uuid
from datetime import datetime, time, timedelta
from django.template.defaultfilters import slugify
from django.conf import settings
import random
from django.forms.models import model_to_dict

from accounts.models import RegisteredUser
from form_builder import form_schema
from form_builder.form_exceptions import DuplicateVariableName, ExpressionCompileError
from form_builder.utils import GeoLocation
from languages.models import Language, Translation
from utilities.timezone_utils import validate_timezone_offset_string

# ---------- Themes ----------
def upload_theme_media(instance, filename):
    return "themes/{}/{}".format(str(instance.code), filename.replace(" ","_"))

class Theme(models.Model):
    """
    Defines a model for form theme.
    A theme consist of set of html templates for various components of the form
    such as base html, various field rendering htmls etc.

    All template html files related to this theme must be kept under the directory
    ``/form_builder/templates/themes/[code]/``


    **The structure of this directory is as follows:**

        - /form_builder/templates/themes/[code]/

            - form_base.html
            - fields

                  - html_text.html
                  - html_numeric.html
                  - html_<widget_name>.html   # Refer 'form_builder.widgets.py'
                  - error_messages.html

    All files under 'fields' directory must essentially define templates for every
    widget variable in form_builder.widgets.FieldWidgets

    A Theme always has a skin with code 'default' which is created by this theme model post save in case it iss absent.

    **Authors**: Gagandeep Singh
    """
    code        = models.SlugField(max_length=64, unique=True, db_index=True, help_text='Theme code used to lookup templates in themes template directory.')
    name        = models.CharField(max_length=256, db_index=True, help_text='Name of the theme as displayed to user.')
    description = models.TextField(null=True, blank=True, help_text='Some description about this theme.')
    icon        = models.ImageField(upload_to=upload_theme_media, help_text='Theme icon as displayed to user')

    active      = models.BooleanField(default=True, help_text='If deactivated, currently using forms will not be affected.')

    created_on  = CreationDateTimeField(db_index=True, help_text='Date on which this theme was created.')
    updated_on  = ModificationDateTimeField(auto_now=False, null=True, blank=True, db_index=True, help_text='Date on which this theme was last updated.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    # Admin Tags
    def fancy_name(self):
        return '<img src="{}" style="height:15px;">&nbsp;&nbsp;{}'.format(self.icon.url, self.name)
    fancy_name.allow_tags = True
    fancy_name.short_description = 'Name'

    # methods
    def get_skin_count(self):
        return self.themeskin_set.all().count()
    get_skin_count.allow_tags = True
    get_skin_count.short_description = 'Skin count'

    def save(self, *args, **kwargs):
        self.code = slugify(self.code)

        if self.id:
            self.updated_on = datetime.now()
        return super(self.__class__, self).save(*args, **kwargs)

def post_save_Theme(sender, instance, **kwargs):
    theme = instance

    # Check if 'Default theme is present
    if not theme.themeskin_set.filter(code='default').exists():
        ThemeSkin.objects.create(
            theme = theme,
            code = 'default',
            name = 'Default',
        )
post_save.connect(post_save_Theme, sender=Theme)

class ThemeSkin(models.Model):
    """
    Defines a model for various skin of a form theme. A skin is essentially a variation in
    look and feel of the page and is mostly defined by css & images.

    All css, js or image files must be kept under the directory
    ``/static/themes/[code]/``
    and must be implemented by ``form_base.html`` of that theme

    By Default, a skin with code ``default`` is created for evert theme by 'Theme' model.

    **Authors**: Gagandeep Singh
    """
    theme       = models.ForeignKey(Theme, db_index=True)
    code        = models.SlugField(max_length=64, db_index=True, help_text='Skin code used as keyword in the form & to loopkup files in theme static directory.')
    name        = models.CharField(max_length=64, db_index=True, help_text='Name of the skin.')
    description = models.TextField(null=True, blank=True, help_text='Some description about this theme.')
    color       = RGBColorField(default=settings.DEFAULT_COLOR,help_text='Primary color for this skin')

    active      = models.BooleanField(default=True, help_text='If deactivated, currently using forms will not be affected.')

    created_on  = CreationDateTimeField(db_index=True, help_text='Date on which this skin was created.')
    updated_on  = ModificationDateTimeField(auto_now=False, null=True, blank=True, db_index=True, help_text='Date on which this skin was last updated.')

    class Meta:
        unique_together = (
            ('theme', 'code'),
            ('theme', 'color')
        )
        ordering = ('theme','name')

    def __unicode__(self):
        return "{} - {}".format(self.theme.name,self.name)



    def save(self, *args, **kwargs):
        if self.id:
            self.updated_on = datetime.now()
        return super(self.__class__, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.code == 'default':
            raise ValidationError("You cannot delete 'default' skin.")

        # NOTE: to prevent cascade delete of the forms,
        # the 'theme' foreignKey has property on_delete=models.PROTECT

        return super(self.__class__, self).delete(*args, **kwargs)

# ---------- Form ----------

class Form(models57.Model):
    """
    Model to define a form.

    **Authors**: Gagandeep Singh
    """
    title           = models.CharField(max_length=255, db_index=True, help_text='Title of the form which is displayed on the top.')
    description     = models.CharField(max_length=512, null=True, blank=True, help_text='(TranslationID) Description about this form.') # tinymce_models.HTMLField(null=True, blank=True, help_text='Description about this form.')
    instructions    = models.CharField(max_length=512, null=True, blank=True, help_text='(TranslationID) Any relevant instructions to fill this form.') # tinymce_models.HTMLField(null=True, blank=True, help_text='Any relevant instructions to fill this form.')
    user_notes      = tinymce_models.HTMLField(null=True, blank=True, help_text='Notes for use use only.')

    theme_skin      = models.ForeignKey(ThemeSkin, on_delete=models.PROTECT, help_text='Theme to be used for this form.')
    languages       = models.ManyToManyField(Language, blank=True, help_text='Languages that are available to the form. English is by default.')

    constants       = JSONField(default=[], null=True, blank=True, help_text='List of constants used in this form.')
    schema          = JSONField(default=[], blank=True, help_text='Form schema in json format.')
    calculated_fields = JSONField(default=[], null=True, blank=True, help_text='List of fields whoes values are calculated dynamically in the form based on a expression. These are calculated in the order of declaration.')

    # Form settings
    timeout         = models.IntegerField(default=None, null=True, blank=True, help_text='Defines the number of seconds after which form expires.')
    show_timer      = models.BooleanField(default=False, help_text='In case \'timeout\' is set, this define whether to show timer or not.')
    randomize       = models.BooleanField(default=False, help_text='Randomize field order. ONLY applicable when there are no conditions.')
    gps_enabled     = models.BooleanField(default=True, help_text="Capture user location while filling form.")
    gps_mandatory   = models.BooleanField(default=False, help_text="If true, the gps location is madatory before form starts.")
    gps_precision   = models.CharField(max_length=16, choices=GeoLocation.choices, default=GeoLocation.FINE, help_text='GPS precision choice. This will automatically set gps config.')
    gps_config      = models57.JSONField(default=None, blank=True, help_text='Gps configurations according to `gps_precision` choice resolved by :class:`form_builder.utils.GeoLocation`.')

    # Meta
    translations    = models57.ListTextField(base_field=models.CharField(max_length=128), null=False, blank=True, help_text="Comma seperated list of translations (languages.Translation) ids.")
    is_ready        = models.BooleanField(default=False, editable=False, help_text='Tells if form is ready to be executed. This is verified on the fact that schema is not empty or [].')
    version         = models.UUIDField(default=uuid.uuid4, db_index=True, help_text='Auto generated form version.')
    created_on      = CreationDateTimeField(db_index=True, help_text='Date on which this form was created.')
    updated_on      = ModificationDateTimeField(auto_now=False, null=True, blank=True, db_index=True, help_text='Date on which this form was last updated.')

    @property
    def schema_obj(self):
        sc_obj = form_schema.load_form_schema(self.schema)
        if self.randomize:
            random.shuffle(sc_obj)

        return sc_obj

    @property
    def constants_obj(self):
        if self.constants is None or self.constants == {}:
            return None
        else:
            return form_schema.load_constant_schema(self.constants)

    @property
    def calculated_fields_obj(self):
        if self.calculated_fields is None or self.calculated_fields == {}:
            return None
        else:
            return form_schema.load_calculated_fields_schema(self.calculated_fields)

    def __unicode__(self):
        return self.title

    # ---- constants ----
    def get_constants_displayable(self):
        constants_obj = self.constants_obj
        if constants_obj is None:
            return None
        else:
            list_constants = [c for c in constants_obj if c.show_on_form]
            return list_constants

    def get_constants_to_include(self):
        constants_obj = self.constants_obj
        if constants_obj is None:
            return None
        else:
            list_constants = [c for c in constants_obj if c.include_in_answers]
            return list_constants

    # ---- Fields ----


    # ---- calculated fields ----
    def get_calc_fields_displayable(self):
        calculated_fields_obj = self.calculated_fields_obj
        if calculated_fields_obj is None:
            return None
        else:
            list_calc_flds = [f for f in calculated_fields_obj if f.show_on_form]
            return list_calc_flds

    def get_calc_fields_to_include(self):
        calculated_fields_obj = self.calculated_fields_obj
        if calculated_fields_obj is None:
            return None
        else:
            list_calc_flds = [f for f in calculated_fields_obj if f.include_in_answers]
            return list_calc_flds

    # --- Form Validator ----
    def validate_form(self):
        """
        Validate form by analyzing schema, unique ids and various other necessary validations and
        return list id translation ids.
        """

        from form_builder.fields import BasicFormField

        set_translation_ids = set()

        if self.description:
            set_translation_ids.add(self.description)

        if self.instructions:
            set_translation_ids.add(self.instructions)

        list_varnames = []
        def push_list_varnames(varname):
            if list_varnames.__contains__(varname):
                raise DuplicateVariableName("Duplicate variable with label '{}'.".format(varname))
            else:
                list_varnames.append(varname)

        # (1) Parse constants JSON & obtain object form.
        constants = self.constants_obj
        if constants:
            for const in constants:
                push_list_varnames(str(const.label))
                if const.text_translation_id is not None:
                    set_translation_ids.add(const.text_translation_id)

        # (2) Parse schema JSON & obtain schema obj. This will check any schema errors.
        schema_obj = self.schema_obj
        if schema_obj is not None and len(schema_obj) != 0:
            # Check if randomization is allowed: There must be no component other than 'fields' if randomize is true
            if self.randomize:
                for comp in schema_obj:
                    if not isinstance(comp, BasicFormField):
                        raise ValidationError("You cannot use randomize since the form contains conditions & layouts.")

            # Prepare field lookup for further use
            lookupDict_fields = {}      # { "<label>": <Field Object>, "<label>":<Field Object>, ...}
            for field in iterate_form_fields(schema_obj):
                label = str(field.label)
                push_list_varnames(label)
                lookupDict_fields[label] = field
                set_translation_ids.update(field.get_translation_ids())

                self.is_ready = True
        else:
            self.is_ready = False

        # (3) Parse calculated fields & obtains object form.
        # Check that all calculated fields are using only constants or mandatory form variables.
        calc_flds = self.calculated_fields_obj
        if calc_flds:
            for calcfld in calc_flds:
                push_list_varnames(str(calcfld.label))
                list_vars_in_expr = calcfld.get_expression_variables()
                if calcfld.text_translation_id is not None:
                    set_translation_ids.add(calcfld.text_translation_id)

                for absolute_var in list_vars_in_expr:
                    varname = absolute_var.replace("$scope.", "").replace("data.", "").replace("constants.", "")
                    if not list_varnames.__contains__(varname):
                        # Check variable was declared or not
                        raise ExpressionCompileError("Undefined variable '{}' in the expression for calculated field '{}'.".format(varname, calcfld.label))
                    else:
                        # Chech if this variable is data field
                        if absolute_var.__contains__("data."):
                            # check if this field is mandatory
                            if lookupDict_fields[varname].required == False:
                                raise ExpressionCompileError("Field '{}' must be mandatory in order to be used in the expression for calculated field '{}'.".format(varname, calcfld.label))

        return list(set_translation_ids)

    # --- Translations ---
    def get_translations(self):
        return Translation.objects.filter(pk__in=self.translations)

    def get_translation_lookup(self):
        list_translations = self.get_translations()
        lookup_dict = { str(trans.pk):trans for trans in list_translations}
        return lookup_dict

    # --- Misc ---
    def humanize_timeout(self):
        secs = self.timeout
        if secs:
            mins, secs = divmod(secs, 60)
            hours, mins = divmod(mins, 60)

            s = []
            s.append(str(hours) + ' hour' + ('s' if hours > 1 else '')) if hours else None
            s.append(str(mins) + ' minute' + ('s' if mins > 1 else '')) if mins else None
            s.append(str(secs) + ' second' + ('s' if secs > 1 else '')) if secs else None
            return ", ".join(s)
        else:
            return None

    def to_json(self):
        data_dict = model_to_dict(self)
        data_dict['languages'] = list(data_dict['languages'].values_list('id', flat=True))
        data_dict['language_codes'] = list(self.languages.all().values_list('code', flat=True))
        for key, val in data_dict.iteritems():
            if isinstance(val, uuid.UUID):
                data_dict[key] = str(val)
            elif isinstance(val, datetime):
                data_dict[key] = val.isoformat()
        return data_dict

    def get_formquestions(self, only_current=True):
        """
        Method to return form questions for this form.
        :param only_current: If True, returns only those questions which are currently in the form.
            Otherwise returns all questions including those which have been changed.
        :return: List<:class:`form_builder.models.FormQuestion`>
        """

        if only_current:
            qry = self.formquestion_set.filter(form_version=self.version)
        else:
            qry = self.formquestion_set.all()
        return qry


    # --- Clean & Save ---
    def clean(self):
        list_translation_ids = self.validate_form()
        # print list_translation_ids
        self.translations = list_translation_ids

        # Gps Settings
        self.gps_config = GeoLocation.config[self.gps_precision]
        if self.gps_enabled == False and self.gps_mandatory == True:
            raise ValidationError("GPS must be enabled before it is marked as mandatory.")

        if self.id:
            self.updated_on = datetime.now()

        super(self.__class__,self).clean()

    def save(self, *args, **kwargs):
        self.clean()

        if self.id:
            self.version = uuid.uuid4()

        #self.validate_form()
        return super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        schema_obj = instance.schema_obj
        if schema_obj is not None and len(schema_obj) != 0:
            for fld in iterate_form_fields(schema_obj):
                print "\tPushing :" , fld.label
                FormQuestion.objects.update_or_create(
                    form_id = instance.id,
                    label = fld.label,
                    field_class = fld._cls,
                    defaults = {
                        "form_version": instance.version,
                        "text_translation_id": fld.text_translation_id,
                        "schema_json": fld.to_json(),
                        "dated": timezone.now()
                    }
                )

                # FormFieldMetaData.objects(
                #     form_id = str(instance.id),
                #     label = fld.label,
                #     field_class = fld._cls
                # ).update_one(
                #     form_version = str(instance.version),
                #     text_ref = fld.text_ref,
                #     text_translation_id = fld.text_translation_id,
                #     required = fld.required,
                #     request_response = fld.request_response,
                #     dated = datetime.now(),
                #     upsert = True
                # )
post_save.connect(Form.post_save, sender=Form)

class FormQuestion(models57.Model):
    """
    Model to store all form questions(fields) irrespective of order or conditions.
    Thus, this model provides flat list of all fields used in the form.

    Moreover, it also keeps a track of previous fields that have been either updated or removed.
    But this model cannot be used as audit trail since, it overrides fields to latest configurations
    if its label & data type class has not been changed.

    **Uniqueness:**

        ``form_id``, ``label``, ``field_class``

    **Logic**:

        - Before inserting new record, table it looked up form any previous record with
          key consisting of (form_id, label, field_class).
        - If found, this record is updated with new configurations settings.
        - If not found, new entry is made. Old one automatically get obsolete as there
          is new record with latest form_version.

    **Points**:

        - To obtains list of all fields currently present in the form, query with
          key (``form_id``, ``form_version``)
        - To obtains list of all fields that are or were in the form, query with
          ``form_id``.

    **Authors**: Gagandeep Singh
    """

    form        = models.ForeignKey(Form, db_index=True, help_text='Form to which this question field belongs to')
    form_version = models.UUIDField(default=uuid.uuid4, db_index=True, help_text='Form version to which this version of field belongs.')
    label       = models.CharField(max_length=255, help_text='Label of the form field.')
    field_class = models.CharField(max_length=128, help_text='Field class of this question.  This must be exactly same as the field class name.')
    text_translation_id = models.CharField(max_length=128, help_text="Raw id of text translation :class:`languages.models.Translation`.")
    schema_json = models57.JSONField(help_text='Json schema of question field as per field class.')

    dated       = models.DateTimeField(db_index=True, help_text='Date on which this record was created/updated.')

    @property
    def translation(self):
        return Translation.objects.with_id(self.text_translation_id)

    class Meta:
        unique_together = ('form', 'label', 'field_class')
        ordering = ['form', 'dated']

    def __unicode__(self):
        return "{}: {}".format(self.form_id, self.label)

'''
class FormFieldMetaData(Document):
    """
    This model maintains the basic information of fields used in a form.
    It also keeps a track of previous fields that have been either updated or removed.
    However, it overrides unchanged fields to latest version and hence this model
    DOES NOT provide full information about previous fields.

    Uniqueness: form_id, label, field_class

    **Logic**:

        - Before inserting new record, collection it looked up form any previous record with
          key consisting of (form_id, label, field_class).
        - If found, this record is updated with remaining information.
        - If not found, new entry is made. Old one automatically get obsolete as there is new
          is new record with latest form_version.

    .. note::
        Current list of field is obtained by querying collection on the key (form_id, form_version)

    **Authors**: Gagandeep Singh
    """

    form_id         = StringField(required=True, unique_with=["label", "field_class"], help_text="Raw ID link to 'Form' model.")
    form_version    = StringField(required=True, help_text="Form version to which this version of field belongs.")
    label           = StringField(required=True, help_text="Label of the form field.")
    field_class     = StringField(required=True, help_text="Class of form field. This must be exactly same as the field class name.")
    text_ref        = StringField(help_text="Text (for reference only) of the form field. WARNING: This may be different than actual text in translation.")
    text_translation_id = StringField(required=True, help_text="Raw id of text translation ('languages.Translation').")
    required        = BooleanField(required=True, help_text="Whether this field must be filled out before submitting the form.")
    request_response = BooleanField(required=True, help_text="If true, user will be requested to answer this field.")

    dated           = DateTimeField(required=True, help_text="Date on which this version of field was created.")

    @property
    def form(self):
        return Form.objects.get(id=int(self.form_id))

    @property
    def translation(self):
        return Translation.objects.with_id(self.text_translation_id)

    meta = {
        "indexes":[
            "form_id",
            "form_version",
            "label",
            "field_class",
            "dated"
        ],
        "ordering": ["form_id", "-dated"]
    }

    def __unicode__(self):
        return "{}: {}".format(self.form_id, self.label)
'''

# ------------ Form Response -----------
class BaseResponse(Document):
    """
    Abstract mongoDb model to store response for a form.

    .. warning::
        This is only an abstract model. This does not map any collection.

    **Authors**: Gagandeep Singh
    """

    # --- Embedded Documents ---
    class UserInformation(EmbeddedDocument):
        """
        Response embedded document to capture user information.

        **Authors**: Gagandeep Singh
        """
        user_id         = StringField(help_text='Primary key of auth.models.user.')
        username        = StringField(help_text='User login username.')
        user_fullname   = StringField(help_text='User full name.')

    class LocationInformation(EmbeddedDocument):
        """
        Response embedded document to capture location information for a response

        **Authors**: Gagandeep Singh
        """
        GPS = 'gps'
        NETWORK_GPS = 'network_gps'
        GEOLOCATION = 'geolocation'
        CH_PROVIDER = (
            (GPS, 'GPS'),
            (NETWORK_GPS, 'Network GPS'),
            (GEOLOCATION, 'GeoLocation')
        )

        provider        = StringField(required=True, choices=CH_PROVIDER, help_text="GPS Provider.")
        coordinates     = GeoPointField(required=True, auto_index=True, help_text='GPS coordinates [longitude,latitude] from which this response was send.')
        accuracy        = FloatField(required=True, help_text='Accuracy (in meters) at which GPS coordinates where captured.')
        timestamp       = LongField(help_text='Timestamp at which gps was taken.')

    class SuspectReason(EmbeddedDocument):
        """
        Response embedded document to record reasons for suspected response.
        **Authors**: Gagandeep Singh
        """
        TYPE_USER_DEFINED = 'user_defined'
        CH_TYPE = (
            (TYPE_USER_DEFINED, 'User defined'),
        )

        id      = StringField(required=True, help_text="GUID for this reason.")
        type    = StringField(required=True, choices=CH_TYPE, help_text='Type of reason.')
        text    = StringField(required=True, help_text="Text describing the reason")
        user_id = StringField(help_text='Primary key of auth.models.user who marked this as suspicious. Empty if marked by the system.')


    class ResponseFlags(EmbeddedDocument):
        """
        Response embedded document to capture various types of flags related to the response.

        **Authors**: Gagandeep Singh
        """
        description_read    = BooleanField(default=False, required=True, help_text='Determines if the description was read by the user')
        instructions_read   = BooleanField(default=False, required=True, help_text='Determines if the instructions were read by the user.')
        suspect             = BooleanField(default=False, required=True, help_text='Determines if this reponse is a suspect. If true, reason must be specified.')
        suspect_reasons     = ListField(help_text='List of reasons is to why this response is a suspect.')
        has_ai              = BooleanField(default=False, help_text='If true, it means this response artifical intelligence applied.')

    class EndPointInformation(EmbeddedDocument):
        """
        Response embedded document to capture various information about response end point.
        An end point is source from where the response originated. It can be a web client,
        a mobile hand-held device or any other device capable to generating response.

        .. warning::
            Do not change end point type enum. These are hardcoded in the device or web client scripts.

        **Authors**: Gagandeep Singh
        """
        WEB_CLIENT = 'web_client'
        MOBILE_DEVICE = 'mobile_device'
        CH_END_POINT = (
            (WEB_CLIENT, 'Web Client'),
            (MOBILE_DEVICE, ' Mobile Device')
        )

        # --- Fields ---
        type            = StringField(required=True, choices=CH_END_POINT, help_text="Type of end point.")

        # Manufacture information
        brand           = StringField(help_text="The consumer-visible brand with which the product/hardware will be associated, if any.")
        model           = StringField(help_text="The end-user-visible name for the end product.")
        manufacturer    = StringField(help_text="The manufacturer of the product/hardware.")
        hardware        = StringField(help_text="The name of the hardware (from the kernel command line or /proc).")

        # Platform
        platform        = StringField(help_text="Device's operating system name i.e. Android/iOS/Windows etc.")
        os_version      = StringField(help_text="Version of the operating system.")
        api_sdk         = StringField(help_text="Api SDK version of the platform.")

        # Hardware Information
        uuid            = StringField(help_text="Device's UUID as determined by the device manufacturer and are specific to the device's platform or model.")
        imei            = StringField(help_text="IMEI (International Mobile Equipment Identity) number of mobile device.")

        # Service Provider
        imsi            = StringField(help_text="IMSI (International Mobile Subscriber Identity) of the SIM used in the device.")
        service_provider = StringField(help_text="Name of the network service provider i.e. Airtel, Vodafone etc.")
        operator_country = StringField(help_text="ISO country code equivalent of the current registered operator's MCC (Mobile Country Code).")

        def __unicode__(self):
            return "{} - {}".format(self.type, self.model)

    class Answer(EmbeddedDocument):
        """
        Response embedded document to an answer to the question in details. This includes
        various meta information for an answer.

        Specifications for ``ai`` field:

            Structure:
            {
                "<algo_key>":{
                    "pending": True/False,
                    "result": {
                        --- result json ---
                    }
                }
            }

            ** Points**:
                - The structure is created during response creation after analyzing corresponding FormField.
                - All process looks for its ``algo_key`` to check if this answer must be analyzed or not. This happens
                  when the process gets a green light to proceed after checking in ``response.process_flags``.
                - If ``algo_key.pending`` is true, it means answer is yet to be procceed, so process it.
                  Otherwise, if false, it means answer must have already been processed.
                - Results are store in ``algo_key.results`` mostly in form of json. Structure varies as per the algorithm result.

        **Authors**: Gagandeep Singh
        """
        question_label  = StringField(required=True, help_text='Label of the question to which this answer is related')
        answer          = BaseField(required=True, help_text='Answer to the question.')
        is_other        = BooleanField(required=True, default=False, help_text='If true, it means the answer of the question belongs to other part of the question.')
        ai              = DictField(default=None, required=False, help_text='AI instructions and result.')

        def __unicode__(self):
            return self.question_label

    class ProcessFlags(EmbeddedDocument):
        """
        Response embedded document to log pending process that are yet to be applied on this response.
        Please note that this is not process logger. It simply specifies what process are still pending.
        Each process search for its key and uses its value to decide whether it must be applied on this response
        or not.

        .. warning::
            This document only contains pending process keys. When the process has been applied, it
            removes its key from this document.

        **Authors**: Gagandeep Singh
        """
        text_analysis   = BooleanField(default=None, required=False, help_text="Used by processes related to text analyzes. If true, it means 'text analysis' is still pending.")



    # --- /Embedded Documents ---

    # Form
    form_id         = StringField(required=True, help_text='Primary key of the form.')
    form_version    = StringField(required=True, help_text='Version of the form.')
    version_obsolete = BooleanField(required=True, help_text='If true, it means this response belongs to older version of the form.')

    # Misc Information
    app_version     = StringField(help_text="Version of the app from which response was send.")
    user            = EmbeddedDocumentField(UserInformation, help_text='User related data.')
    end_point_info  = EmbeddedDocumentField(EndPointInformation, required=True, help_text="Device information")
    language_code   = StringField(default=Language.DEFAULT_LANGUAGE_CODE, required=True, help_text="Code of the language used while responding.")

    # Response Data
    response_uid    = StringField(required=True, unique=True, help_text='Response unique id as send from device.')
    constants       = DictField(help_text='Dictionary of all constants & their values as used in form.')
    answers         = DictField(required=True, help_text='Dictionary containing answer for questions asked in the form.')
    answers_other   = DictField(help_text='Dictionary containing answer for other option of the questions.')
    list_answers    = EmbeddedDocumentListField(Answer, help_text="List of answers and other answer along with their meta details. These are indexed. These are populated by 'answers'.")
    calculated_fields = DictField(help_text='Dictionary of calculated fields as evaluated by the form.')

    # Time Dimension
    timezone_offset = StringField(required=True, max_length=5, help_text="Client's timezone in format [+/-]HHMM e.i. +0530")
    response_date   = DateTimeField(required=True, help_text='Date on which user responded.')
    start_time      = DateTimeField(required=True, help_text='Datetime at which user started filling the form.')
    end_time        = DateTimeField(required=True, help_text='Datetime at which user started finished filling the form.')
    duration        = FloatField(required=True, help_text='Time (In sec) taken by user to fill this form. This must be equal to (end_time-start_time).')

    # Space Dimension
    location        = EmbeddedDocumentField(LocationInformation, help_text='Location related data.')

    # Metadata
    flags = EmbeddedDocumentField(ResponseFlags, required=True, help_text='Various information signalizing something related to this response.')

    # Process
    process_flags   = EmbeddedDocumentField(ProcessFlags, help_text='Flags containing logs for process that are yet to be applied.As the process get completed, key is marked false.')

    # Dates
    created_on      = DateTimeField(default=datetime.now, required=True, help_text='Date on which this record was created in the database.')
    updated_on      = DateTimeField(default=None, help_text='Date on which this record was modified.')

    meta = {
        'abstract': True,
        'indexes':[
            'form_id',
            # 'version_obsolete',
            'app_version',
            # 'user.user_id',
            'user.username',
            'end_point_info.type',
            'response_uid',
            'list_answers.question_label',
            'list_answers.answer',
            'list_answers.is_other',
            'flags.suspect',
            # 'timezone_offset',
            '-response_date',
            '-created_on',
            {
                'fields': ['process_flags.text_analysis'],
                'sparse': True,
                'cls': False
            }
        ]
    }

    def __unicode__(self):
        return "{} - {}".format(self.form_id, str(self.pk))

    def get_respondent(self):
        """
        Method to get respondent that is, :class:`accounts.models.RegisteredUser` instance.

        **Authors**: Gagandeep Singh
        """
        return RegisteredUser.objects.get(user__username=self.user.username)

    def get_form(self):
        """
        Method to get form to which this response belongs to.
        :return: Instance of :class:`form_builder.models.Form`
        """
        return Form.objects.get(id=self.form_id)

    def get_duration_time(self):
        """
        Method to return duration in time format HH:MM:SS.

        **Authors**: Gagandeep Singh
        """
        time_format = str(timedelta(seconds=self.duration)).split('.')[0]
        return time_format

    def get_answers_lookup(self):
        """
        Method to get answer lookup dictionary that contains each answer information in detail.
        This uses ``response.list_answers`` to create lookup dict.
        :return: Lookup dict for format: { "<label>": { <Answer embedded doc> } }
        """

        lookup_dict = {ans.question_label:ans for ans in self.list_answers}
        return lookup_dict

    def suspicion_add(self, type, text, user_id):
        """
        Method to add suspicion to this response.
        :param type: Type of suspicion
        :param text: text of suspicion
        """

        suspicion = BaseResponse.SuspectReason(
            id =str(uuid.uuid4()),
            type = type,
            text = text,
            user_id = str(user_id)
        )
        self.flags.suspect_reasons.append(suspicion)
        self.flags.suspect = True
        self.save()

    def suspicion_remove(self, reason_id):
        """
        Method to remove a suspicion reason.

        :param reason_id: Reason id to be removed
        :return: True if successful, False if id not found

        **Authors**: Gagandeep Singh
        """

        success = False
        item = None
        for idx, rsn in enumerate(self.flags.suspect_reasons):
            if rsn.id == reason_id:
                item = rsn
                break

        if item:
            self.flags.suspect_reasons.remove(item)

            if len(self.flags.suspect_reasons) == 0:
                self.flags.suspect = False

            self.save()

            success = True

        return success


    def save(self, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            self.updated_on = datetime.now()

        # Timezone validation
        if not validate_timezone_offset_string(self.timezone_offset):
            raise ValidationError("Invalid timezone offset string '{}'. Correct format '[+/-]HHMM'.".format(self.timezone_offset))

        # Flags
        if self.flags.suspect and len(self.flags.suspect_reasons) == 0:
            raise Exception('Please specify atleast one reason is to why this response is a suspect.')

        if self.pk is None:
            # Cache all current form questions
            cache_curr_questions = {}
            form = self.get_form()
            for fq in form.get_formquestions(only_current=True): # Current questions
                cache_curr_questions[fq.label] = fq
            # Old questions must not be included since processing for them has now been turned off.
            # if str(form.version) != self.form_version:
            #     for fq in form.formquestion_set.filter(form_version=self.form_version): # Replace, as per this response form version
            #         cache_curr_questions[fq.label] = fq

            # Process flags
            text_analysis = False

            list_answers = []

            # (a) Add answers to list_answers
            for ques_label,answer in self.answers.iteritems():
                fq = cache_curr_questions.get(ques_label, None)  # None in case contants or calculated_fields were included in the answers

                # Check all AI that are to be applied on this field.
                # This is completely based on current questions only.
                has_ai = False
                if fq and fq.schema_json.get('ai_directives', None):
                    ai = {}
                    for algo_key, val in fq.schema_json['ai_directives'].iteritems():
                        if val is True:
                            ai[algo_key] = {
                                "pending": True
                            }
                            has_ai = True
                            text_analysis = True    # TODO: Check process type (text/image) before setting this

                if isinstance(answer, list):
                    # Answer is an arra of value
                    list_values = answer
                else:
                    # Purposely make it array of value
                    list_values = [answer]

                # Add separate entry for each value of the answer.
                for ans in list_values:
                    answer_doc = BaseResponse.Answer(
                        question_label = ques_label,
                        answer = ans
                    )
                    if has_ai:
                        answer_doc.ai = ai

                    list_answers.append(answer_doc)

            # (b) Add 'other' answers to list_answers
            for ques_label, ans in self.answers_other.iteritems():
                answer_doc = BaseResponse.Answer(
                    question_label = ques_label,
                    answer = ans,
                    is_other = True
                )

                if has_ai:
                        answer_doc.ai = ai

                list_answers.append(answer_doc)

            # Update variable
            self.list_answers = list_answers

            # Set process flags
            if text_analysis:
                process_flags = BaseResponse.ProcessFlags(
                    text_analysis = text_analysis
                )
                self.process_flags = process_flags

                self.flags.has_ai = True

        return super(BaseResponse, self).save(*args, **kwargs)


# ------------ /Form Response -----------

# ---------- Global methods ----------
def iterate_form_fields(schema):
    """
    Global method to recursively iterate over fields in form schema.

    :param schema: Form schema
    :return: Field

    **Authors**: Gagandeep Singh
    """
    from form_builder import fields
    from form_builder import conditions
    from form_builder import layouts

    for node in schema:
        if isinstance(node, fields.BasicFormField):
            # print node.label
            yield node
        elif isinstance(node, conditions.BaseCondition):
            if isinstance(node, conditions.BinaryCondition):
                for fld in iterate_form_fields(node.true_branch.children_obj):
                    yield fld
                if node.false_branch is not None:
                    for fld in iterate_form_fields(node.false_branch.children_obj):
                        yield fld
            elif isinstance(node, conditions.SwitchCondition):
                for branch in node.list_branches:
                    for fld in iterate_form_fields(branch.children_obj):
                        yield fld
                if node.use_default:
                    for fld in iterate_form_fields(node.default_branch.children_obj):
                        yield fld
        elif isinstance(node, layouts.BaseLayout):
            if isinstance(node, layouts.SectionLayout):
                for fld in iterate_form_fields(node.children_obj):
                    yield fld