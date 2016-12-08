# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from __future__ import unicode_literals

from django.db import models
import tinymce.models as tinymce_models
from django_mysql.models import Model, ListTextField
from django_extensions.db.fields.json import JSONField
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from colorful.fields import RGBColorField
from django.db.models.signals import post_save

from mongoengine.document import *
from mongoengine.fields import *

from django.core.exceptions import ValidationError
import uuid
from datetime import datetime, time
from django.template.defaultfilters import slugify
from django.conf import settings
import random
from django.forms.models import model_to_dict

from form_builder import form_schema
from form_builder.form_exceptions import DuplicateVariableName, ExpressionCompileError
from languages.models import Language, Translation

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

class Form(Model):
    """
    Model to define a form.

    **Authors**: Gagandeep Singh
    """
    title           = models.CharField(max_length=255, db_index=True, help_text='Title of the form which is displayed on the top.')
    description     = models.CharField(max_length=512, null=True, blank=True, help_text='(TranslationID) Description about this form.') # tinymce_models.HTMLField(null=True, blank=True, help_text='Description about this form.')
    instructions    = models.CharField(max_length=512, null=True, blank=True, help_text='(TranslationID) Any relevant instructions to fill this form.') # tinymce_models.HTMLField(null=True, blank=True, help_text='Any relevant instructions to fill this form.')
    user_notes      = tinymce_models.HTMLField(null=True, blank=True, help_text='Notes for use use only.')

    theme_skin      = models.ForeignKey(ThemeSkin, on_delete=models.PROTECT, help_text='Theme to be used for this form.')
    languages       = models.ManyToManyField(Language, help_text='Languages that are available to the form. English is by default.')

    constants       = JSONField(null=True, blank=True, help_text='List of constants used in this form.')
    schema          = JSONField(help_text='Form schema in json format.')
    calculated_fields = JSONField(null=True, blank=True, help_text='List of fields whoes values are calculated dynamically in the form based on a expression. These are calculated in the order of declaration.')

    # Form settings
    timeout         = models.IntegerField(default=None, null=True, blank=True, help_text='Defines the number of seconds after which form expires.')
    show_timer      = models.BooleanField(default=False, help_text='In case \'timeout\' is set, this define whether to show timer or not.')
    randomize       = models.BooleanField(default=False, help_text='Randomize field order. ONLY applicable when there are no conditions.')
    gps_enabled     = models.BooleanField(default=True, help_text="Capture user location while filling form.")
    gps_required    = models.BooleanField(default=False, help_text="If true, the gps location is madatory before form starts.")
    gps_high_accuracy = models.BooleanField(default=True, help_text="If true, attempts to retrieve position using device gps otherwise, uses network-based methods.")
    gps_max_radius  = models.IntegerField(null=True, blank=True, help_text='Max radius (in meters) that is acceptable for captured location.')
    gps_max_age_allowed = models.IntegerField(default=10000, null=True, blank=True, help_text="Max age (in milliseconds) of GPS allowed to be used if capturing fails.")

    # Meta
    translations    = ListTextField(base_field=models.CharField(max_length=128), null=False, blank=True, help_text="Comma seperated list of translations (languages.Translation) ids.")
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
                set_translation_ids.add(const.text_translation_id)

        # (2) Parse schema JSON & obtain schema obj. This will check any schema errors.
        schema_obj = self.schema_obj

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

        # (3) Parse calculated fields & obtains object form.
        # Check that all calculated fields are using only constants or mandatory form variables.
        calc_flds = self.calculated_fields_obj
        if calc_flds:
            for calcfld in calc_flds:
                push_list_varnames(str(calcfld.label))
                list_vars_in_expr = calcfld.get_expression_variables()
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
        data_dict['language_codes'] = list(self.languages.all().values_list('code', flat=True))
        for key, val in data_dict.iteritems():
            if isinstance(val, uuid.UUID):
                data_dict[key] = str(val)
            elif isinstance(val, datetime):
                data_dict[key] = val.isoformat()
        return data_dict


    # --- Clean & Save ---
    def clean(self):
        list_translation_ids = self.validate_form()
        # print list_translation_ids
        self.translations = list_translation_ids

        # Gps Settings
        if self.gps_enabled == False and self.gps_required == True:
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
        for fld in iterate_form_fields(instance.schema_obj):
            print "\tPushing :" , fld.label
            FormFieldMetaData.objects(
                form_id = str(instance.id),
                label = fld.label,
                field_class = fld._cls
            ).update_one(
                form_version = str(instance.version),
                text_ref = fld.text_ref,
                text_translation_id = fld.text_translation_id,
                required = fld.required,
                request_response = fld.request_response,
                dated = datetime.now(),
                upsert = True
            )
post_save.connect(Form.post_save, sender=Form)

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
        - If not found, new entry is made. Old one automatically get obselete as there is new
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