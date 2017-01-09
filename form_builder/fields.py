# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from jsonobject import *
from datetime import datetime, date, time
import random
import copy, json

from jsonobject.base_properties import DefaultProperty

import validators
from form_exceptions import *
from widgets import *
from languages.models import Translation


#TODO: Add 'validate_value' method in all fields

class DataType:
    """
    Enum class for data types used in the form.

    .. warning::
        Some of these static variables have been used in 'MCQ_Types' which have been referenced using
        values instead of variable. Please be careful will making any amendments.

    **usage**:

        - form_builder/templates/themes/<theme_name>/fields/choice_other.html

    **Authors**: Gagandeep Singh
    """
    STRING = 'string'
    INT = 'int'
    FLOAT = 'float'
    BOOL = 'bool'
    DATE = 'date'
    TIME = 'time'
    DATETIME = 'datetime'

    choices = (
        (STRING, 'String'),
        (INT, 'Integer'),
        (FLOAT, 'Decimal'),
        (BOOL, 'Boolean'),
        (DATE, 'Date'),
        (TIME, 'Time'),
        (DATETIME, 'Datetime')
    )

    @staticmethod
    def get_python_class(type):
        """
        Returns a python data type for a form data type.

        :param type: Form type as in :class:`form_builder.fields.DataType`
        :return: Python type

        **Authors**: Gagandeep Singh
        """
        if type == DataType.STRING:
            return str
        elif type == DataType.INT:
            return int
        elif type == DataType.FLOAT:
            return float
        elif type == DataType.BOOL:
            return bool
        elif type == DataType.DATE:
            return date
        elif type == DataType.TIME:
            return time
        elif type == DataType.DATETIME:
            return datetime
        else:
            raise ValueError("Invalid data-type {}.".format(type))


class MCQ_Types:
    """
    Enum class for data types allowed for MCQ questions. These are subset of :class:`form_builder.fields.DataType`.

    .. warning::
        Please read :class:`form_builder.fields.DataType` warning before making any changes.

    **Authors**: Gagandeep Singh
    """
    STRING = DataType.STRING
    INT = DataType.INT
    FLOAT = DataType.FLOAT

    choices = (
        (STRING, 'Alphanumeric'),
        (INT, 'Number'),
        (FLOAT, 'Decimal')
    )

class ChoiceOrder:
    """
    Enum class for types of ordering in choice fields.

    **Authors**: Gagandeep Singh
    """
    ASCENDING = 'ascending'
    DESCENDING = 'descending'
    RANDOM = 'random'
    DEFAULT = 'default'

    choices = (
        (DEFAULT, 'Default'),
        (ASCENDING, 'Ascending'),
        (DESCENDING, 'Descending'),
        (RANDOM, 'Random'),
    )

class OtherOptionType:
    """
    Enum class for types of questions asked when other option is selected for a MCQ question.

    **Authors**: Gagandeep Singh
    """
    SINGLE_LINE = 'single_line'
    PARAGRAPH = 'paragraph'

    choices = (
        (SINGLE_LINE, 'Single Line'),
        (PARAGRAPH, 'Paragraph')
    )


# ---------- Embedded Classes ----------
class Choice(JsonObject):
    """
    Define a simple choice (with value & text) for a multiple choice field.

    **Authors**: Gagandeep Singh
    """
    value = DefaultProperty(required=True)  # Value that is relieved as an answer to the question
    text = StringProperty(required=True)    # Text displayed for the option o the user


class AiTextDirectives(JsonObject):
    """
    Defines AI(text analysis) directives to applied on an answer.

    .. note::
        Only applicable on answer type of type text.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    text_sentiment   = BooleanProperty(default=False, required=True)     # Determine if text is positive or negative.
    text_emotion     = BooleanProperty(default=False, required=True)     # Predict emotion expressed in the answer.
    text_personality = BooleanProperty(default=False, required=True)     # Predict personality traits.
    text_personas    = BooleanProperty(default=False, required=True)     # Predicts the Myers Briggs persona

class AiImageDirectives(JsonObject):
    """
    Defines AI(Image analysis) directives to applied on an photo answer.

    .. note::
       Only applicable for answer types of type photo.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    img_object_and_scene_detection  = BooleanProperty(default=False, required=True)     # Identifies thousands of objects in captured image

# ---------- Generic Field ----------
# Points:
#   * Add new field:
#       - Always extend  'BasicFormField' to define field type
#       - Widget: Add widget(s) for this field in 'form_builder.widgets.py'
#       - Form designer: create partial templates for this field:
#           /static/templates/form_builder/
#               |--- look-n-feel
#               |       |--- html_<widget_name>.html    # Refer 'form_builder.widgets.py'
#           form_builder.templates
#               |--- partials
#                       |--- editor
#                               |--- <class_name>.html  (Manually change default values here)
#               |--- form_builder
#                       | --- form_designer.html
#                               Controller: QuestionSchemaController, inside '$scope.remove_question'
#                               Add condition to remove all translation when this field is deleted
#       - Theme: For each theme, create a template for this field. Refer 'form_builder.models.Theme' model comment.

class BasicFormField(JsonObject):
    """
    An abstract field that defines basic definition of a field in a form. Inherit this class to create any field.

    .. note::

        All form fields inherit this fields that is, every form field is type of BasicFirmField.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    _cls_base = StringProperty(default='BasicFormField', required=True)
    _cls = StringProperty(name='_cls', required=True)   # Name of this class
    label = StringProperty(required=True, validators=[validators.validate_label])       # Unique label within the form) of the field.
    text_ref = StringProperty()        # Question text associated with this field. WARNING: for reference use only
    text_translation_id = StringProperty(required=True)  # (TranslationID) Text of the question
    required = BooleanProperty(required=True, default=False)   # Whether this field must be filled out before submitting the form.
    request_response = BooleanProperty(required=True, default=False)    # If true, user will be requested to answer this field
    description = StringProperty(default=None)  # (TranslationID) Description for this field
    # placeholder = StringProperty(default=None) # (TranslationID) Guide text for this field. This will appear as placeholder.
    default_error_message = StringProperty(default=None) # (TranslationID) Override default message to be displayed answer is required
    user_notes = StringProperty()   # User notes for this field
    widget = StringProperty(required=True, choices=FieldWidgets.choices_text, default=FieldWidgets.HTML_TEXT)

    @property
    def translation(self):
        """
        Returns translation for question text.

        :return: :class:`languages.models.Translation` instance.

        **Authors**: Gagandeep Singh
        """
        return Translation.objects.with_id(self.text_translation_id)

    def __init__(self, _obj=None, **kwargs):
        # (1) Check '_cls' in _obj or kwargs
        this_class = self.__class__.__name__
        obj_cls = None
        if _obj is not None:
            obj_cls = _obj.get('_cls',None)
        else:
            obj_cls = kwargs.get('_cls',None)

        if obj_cls:
            if obj_cls != this_class:
                raise FieldDefinitionError("Form class mismatch. Using class '{}'".format(obj_cls))
        else:
            obj_cls = this_class

        # (2) Update Kwargs
        kwargs.update({
            "_cls": obj_cls
        })
        super(BasicFormField, self).__init__(_obj=_obj, **kwargs)

        # if self.required:
        #     if self.default_error_message is None:
        #         raise FieldDefinitionError("Please enter default error message")

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.label)

    def get_classname(self):
        return self._cls

    def get_translation_ids(self):
        """
        Get all translations used in this field.

        :return: List<:class:`languages.model.Translation`>

        **Authors**: Gagandeep Singh
        """
        list_translation_ids = [self.text_translation_id]

        if self.description:
            list_translation_ids.append(self.description)

        if self.default_error_message:
            list_translation_ids.append(self.default_error_message)

        return list_translation_ids

    def validate_value(self, value):
        """
        Validate value as the answer for question of this form field.
        Throws :class:`form_builder.form_exceptions.FieldValueError`.

        :param value: Value

        **Authors**: Gagandeep Singh
        """
        if self.required:
            if value is None or value == '':
                raise FieldValueError("Value cannot be empty.")

    def to_json(self):
        """
        Get json form for this field.

        :return: JSON

        **Authors**: Gagandeep Singh
        """
        self.text_ref = self.translation.sentence

        # ----- Hack -----
        # self._obj for all fields inside layouts contains contains `_obj`, `_type_config`, `_wrapper` from nowhere
        # removing these causes schema load error. The `to_json()` function uses `_obj` to create json which throws errors
        # when these attributes are found.
        if hasattr(self._obj, '_wrapper'):
            self.validate()
            field_dict = dict(self._obj)
            return json.loads(json.dumps(field_dict))
        # ----- /Hack -----

        return super(BasicFormField, self).to_json()

# ---------- /Generic Field ----------

# ---------- Fundamental FormFields ----------
class TextFormField(BasicFormField):
    """
    Defines a single-line text field.

    **Authors**: Gagandeep Singh
    """
    min_length = IntegerProperty(default=0)                 # Minimum number of letters allowed.
    max_length = IntegerProperty(default=128)               # Maximum number of letters allowed.
    allow_special_chars = BooleanProperty(required=True, default=True)     # Allow special characters (Anything other than a-zA-Z0-9).

    def __init__(self, _obj=None, **kwargs):
        super(TextFormField, self).__init__(_obj=_obj, **kwargs)

        # validate min-max length values
        if self.min_length is not None and self.max_length is not None:
            validators.min_max_validator(self.min_length, self.max_length)

    def validate_value(self, value):
        super(TextFormField,self).validate_value(value)

        if value is None or value == '':
            # Check for special characters
            if not self.allow_special_chars:
                validators.validate_no_special_char(value)

class EmailFormField(TextFormField):
    """
    Defines an email form field.

    **Authors**: Gagandeep Singh
    """
    max_length = IntegerProperty(default=254)
    widget = StringProperty(required=True, choices=FieldWidgets.choices_email, default=FieldWidgets.HTML_EMAIL)

    def __init__(self, _obj=None, **kwargs):
        super(TextFormField, self).__init__(_obj=_obj, **kwargs)

        self.min_length = None
        self.allow_special_chars = True


    def validate_value(self, value):
        super(EmailFormField,self).validate_value(value)
        if self.required:
            validators.validate_email(value)

class PasswordFormField(TextFormField):
    """
    Defines a password form field.

    **Authors**: Gagandeep Singh
    """
    allow_alphabets = BooleanProperty(required=True, default=True)  # Allow alphabets in the password
    allow_numbers = BooleanProperty(required=True, default=True)    # Allow numbers in the password
    # - allow_special_chars  - Already defined in TextFormField

    widget = StringProperty(required=True, choices=FieldWidgets.choices_password, default=FieldWidgets.HTML_PASSWORD)

    def get_pattern(self):
        char_set = ''

        if self.allow_alphabets:
            char_set += 'a-zA-Z'
        if self.allow_numbers:
            char_set += '\\d'
        if self.allow_special_chars:
            char_set += '\\W'

        return "/^[" + char_set + "]+$/"

    def get_pattern_error(self):
        char_set_names = []
        if self.allow_alphabets:
            char_set_names.append('alphabets')
        if self.allow_numbers:
            char_set_names.append('numbers')
        if self.allow_special_chars:
            char_set_names.append('special characters')

        return "Please use {} only.".format(", ".join(char_set_names))

class TextAreaFormField(BasicFormField):
    """
    Defines a multi-line text field that can hold a reasonable number of characters.

    **Authors**: Gagandeep Singh
    """
    min_length = IntegerProperty(default=0)                 # Minimum number of letters allowed.
    max_length = IntegerProperty(default=1000)              # Maximum number of letters allowed.
    widget = StringProperty(required=True, choices=FieldWidgets.choices_textarea, default=FieldWidgets.HTML_TEXTAREA)
    ai_directives = ObjectProperty(AiTextDirectives)    # AI directives for an answer to this question

    def __init__(self, _obj=None, **kwargs):
        super(TextAreaFormField, self).__init__(_obj=_obj, **kwargs)

        # validate min-max length values
        if self.min_length is not None and self.max_length is not None:
            validators.min_max_validator(self.min_length, self.max_length)

class NumberFormField(BasicFormField):
    """
    Defines a numeric field for entering a integer values only.

    **Authors**: Gagandeep Singh
    """
    min_length = IntegerProperty(default=0)                 # Minimum number of letters allowed.
    max_length = IntegerProperty(default=5)                 # Maximum number of letters allowed.
    allow_negative = BooleanProperty(required=True, default=True)          # Whether to allow any negative values
    min_value = IntegerProperty()                           # Minimum integer value that the field can hold
    max_value = IntegerProperty()                           # Maximum integer value that the the field can hold
    widget = StringProperty(required=True, choices=FieldWidgets.choices_number, default=FieldWidgets.HTML_NUMBER)

    def __init__(self, _obj=None, **kwargs):
        super(NumberFormField, self).__init__(_obj=_obj, **kwargs)

        # validate min-max length values
        if self.min_length is not None and self.max_length is not None:
            validators.min_max_validator(self.min_length, self.max_length)

        # validate field min-max values
        if self.min_value is not None and self.max_value is not None:
            validators.min_max_validator(self.min_value, self.max_value)

        # check if 'min_value' is not less than 0 if 'allow_negative' is false
        if self.min_value is not None:
            if not self.allow_negative and self.min_value < 0:
                raise FieldDefinitionError("Minimum value cannot be less than 0 since negatives are not allowed.")

    def get_min_value(self):
        """
        Returns minimum possible value this field can have
        depending upon 'allow_negative' & 'min_value'

        :return: Minimuim value

        **Authors**: Gagandeep Singh
        """
        if self.min_value is None:
            if self.allow_negative:
                return None
            else:
                return 0
        else:
            if self.allow_negative:
                return self.min_value
            else:
                return max(0, self.min_value)



class DecimalFormField(BasicFormField):
    """
    Defines a field for entering a decimal as well as integer values.
    All integer values will be converted to decimal.

    **Authors**: Gagandeep Singh
    """
    max_integer_length = IntegerProperty(required=True, default=5)         # Maximum length of integer part; Minimum is default 1 which is value 0
    max_decimal_length = IntegerProperty(required=True, default=2)         # Maximum precision of decimal part
    allow_negative = BooleanProperty(required=True, default=True)          # Whether to allow any negative values
    min_value = DecimalProperty()                           # Minimum decimal value that the field can hold
    max_value = DecimalProperty()                           # Maximum decimal value that the the field can hold
    widget = StringProperty(required=True, choices=FieldWidgets.choices_decimal, default=FieldWidgets.HTML_NUMBER_DECIMAL)

    def __init__(self, _obj=None, **kwargs):
        super(DecimalFormField, self).__init__(_obj=_obj, **kwargs)

        # validate field min-max values
        if self.min_value is not None and self.max_value is not None:
            validators.min_max_validator(self.min_value, self.max_value)

        # check if 'min_value' is not less than 0 if 'allow_negative' is false
        if self.min_value is not None:
            if not self.allow_negative and self.min_value < 0:
                raise FieldDefinitionError("Minimum value cannot be less than 0 since negatives are not allowed.")

    def get_steps(self):
        return 1.0 / (10**self.max_decimal_length)

    def get_max_length(self):
        """
        Return maximum input length of this field, which is
        integer count + 1 + decimal count
        :return:
        """
        return self.max_integer_length + 1 + self.max_decimal_length

    def get_min_value(self):
        """
        Returns minimum possible value this field can have
        depending upon 'allow_negative' & 'min_value'
        :return:
        """
        if self.min_value is None:
            if self.allow_negative:
                return None
            else:
                return 0
        else:
            if self.allow_negative:
                return self.min_value
            else:
                return max(0, self.min_value)

class DateFormField(BasicFormField):
    """
    Defines a date field. Date is stored as YYYY-MM-DD.

    **Authors**: Gagandeep Singh
    """
    widget = StringProperty(required=True, choices=FieldWidgets.choices_date, default=FieldWidgets.HTML_DATE)

class TimeFormField(BasicFormField):
    """
    Defines a time field. Time is stored as HH:MM:SS.

    **Authors**: Gagandeep Singh
    """
    widget = StringProperty(required=True, choices=FieldWidgets.choices_time, default=FieldWidgets.HTML_TIME)

class DateTimeFormField(BasicFormField):
    """
    Defines a datetime form field that stores date as well as time together.

    **Authors**: Gagandeep Singh
    """
    widget = StringProperty(required=True, choices=FieldWidgets.choices_datetime, default=FieldWidgets.HTML_DATEIME_LOCAL)


class BinaryFormField(BasicFormField):
    """
    Defines a binary choice field with only 2 options, one for true and other for false.

    **Authors**: Gagandeep Singh
    """
    choice_type = MCQ_Types.STRING

    true_value = StringProperty(required=True, default='Yes')   # Value of true option
    true_text = StringProperty(required=True, default='Yes')    # Text for true option
    false_value = StringProperty(required=True, default='No')   # Value of false option
    false_text = StringProperty(required=True, default='No')    # Text for false option
    # default_selection = BooleanProperty()                       # What is selected as default. If None, nothing is selected
    widget = StringProperty(required=True, choices=FieldWidgets.choices_binary, default=FieldWidgets.RADIO_BTNGRP_HORIZONTAL)

    def iterate_choices(self):
        return [
            {"value": self.true_value, "text": self.true_text},
            {"value": self.false_value, "text": self.false_text}
        ]

    def get_all_choice_values(self):
        list_choices = [self.true_value, self.false_value]
        return list_choices

class MCSSFormField(BasicFormField):
    """
    Defines a 'Multiple Choice Single Select' field that will show multiple choices
    from which only one choice can be selected as answer.

    **Authors**: Gagandeep Singh
    """
    choice_type = StringProperty(required=True, default=MCQ_Types.STRING, choices=MCQ_Types.choices)
    list_choices = ListProperty(Choice,required=True)    # List of choices of form [{"value":"<value>", "text":"<text>"}, ... ]
    choice_ordering = StringProperty(required=True, default=ChoiceOrder.DEFAULT, choices=ChoiceOrder.choices)   # Order in which choice are to be displayed
    allow_other = BooleanProperty(required=True, default=False)             # If True, choice will have 'Other' option which on selection will allow user to type custom value
    other_value = StringProperty(default='Other')           # Value for other option if allowed
    other_text = StringProperty(default='Other')            # Text for other option if allowed
    other_question = StringProperty(default='Please enter your choice')     # Question to be asked when other is selected
    # other_option_type = StringProperty(default=OtherOptionType.SINGLE_LINE)     # Field Type of other option
    widget = StringProperty(required=True, choices=FieldWidgets.choices_mcss, default=FieldWidgets.HTML_RADIO)

    def __init__(self, _obj=None, **kwargs):
        super(MCSSFormField, self).__init__(_obj=_obj, **kwargs)

        # Validate 'list_choice' keys according to 'choice_type'
        if self.choice_type == MCQ_Types.STRING:
            type_validator = validators.string_choices
        elif self.choice_type == MCQ_Types.INT:
            type_validator = validators.int_choices
        elif self.choice_type == MCQ_Types.FLOAT:
            type_validator = validators.float_choices
        else:
            raise FieldDefinitionError("Invalid choice type '{}'".format(self.choice_type))

        type_validator(self.list_choices)

        # Validate if 'allow_other' is selected
        if self.allow_other:
            if self.other_value is None or self.other_text is None:
                raise FieldDefinitionError("Please set 'other_value' and 'other_text'.")
            else:
                # Check if 'list_choices' does not have 'other_value'
                if self.other_value in self.get_choice_keys():
                    raise FieldDefinitionError("Choice list cannot have '{}' since it is already used as 'Other' option.".format(self.other_value))

            # if self.other_option_type is None:
            #     raise FieldDefinitionError("Please select option type.")
            if self.other_question is None:
                raise FieldDefinitionError("Please enter the question to be asked when other is selected.")

    def get_choice_keys(self):
        return [ch.value for ch in self.list_choices]

    def iterate_choices(self):
        if self.choice_ordering == ChoiceOrder.ASCENDING:
            ordered_list_choices = sorted(self.list_choices, key = lambda ch: ch['value'])
        elif self.choice_ordering == ChoiceOrder.DESCENDING:
            ordered_list_choices = sorted(self.list_choices, key = lambda ch: ch['value'], reverse=True)
        elif self.choice_ordering == ChoiceOrder.RANDOM:
            ordered_list_choices = [ch for ch in self.list_choices]
            random.shuffle(ordered_list_choices)
        else:
            ordered_list_choices = self.list_choices

        return ordered_list_choices

    def get_all_choice_values(self):
        list_choices = [ch['value'] for ch in self.list_choices]
        if self.allow_other:
            list_choices.append(self.other_value)

        return list_choices


class MCMSFormField(BasicFormField):
    """
    Defines a 'Multiple Choice Multiple Select' field that will show multiple choices
    from which n-number of choices can be selected as answer.

    **Authors**: Gagandeep Singh
    """
    choice_type = StringProperty(required=True, default=MCQ_Types.STRING, choices=MCQ_Types.choices)
    # list_choices = DictProperty(required=True, validators=[validators.validate_choices])       # Dictionary of choices of form {"<value>":"<value text>", ... }
    list_choices = ListProperty(Choice,required=True)    # List of choices of form [{"value":"<value>", "text":"<text>"}, ... ]
    choice_ordering = StringProperty(required=True, default=ChoiceOrder.DEFAULT, choices=ChoiceOrder.choices)   # Order in which choice are to be deisplayed
    min_selection = IntegerProperty()           # Minimum number of choices that must be selected
    max_selection = IntegerProperty()           # Maximum number of choices that can be selected; greater than 'min_selection'
    allow_other = BooleanProperty(required=True, default=False)             # If True, choice will have 'Other' option which on selection will allow user to type custom value
    other_value = StringProperty(default='Other')           # Value for other option if allowed
    other_text = StringProperty(default='Other')            # Text for other option if allowed
    other_question = StringProperty(default='Please enter your choice')     # Question to be asked when other is selected
    # other_option_type = StringProperty(default=OtherOptionType.SINGLE_LINE)     # Field Type of other option
    widget = StringProperty(required=True, choices=FieldWidgets.choices_mcms, default=FieldWidgets.HTML_CHECKBOX)

    def __init__(self, _obj=None, **kwargs):
        super(MCMSFormField, self).__init__(_obj=_obj, **kwargs)

        len_choices = len(self.list_choices)

        # Validate 'list_choice' keys according to 'choice_type'
        if self.choice_type == MCQ_Types.STRING:
            type_validator = validators.string_choices
        elif self.choice_type == MCQ_Types.INT:
            type_validator = validators.int_choices
        elif self.choice_type == MCQ_Types.FLOAT:
            type_validator = validators.float_choices
        else:
            raise FieldDefinitionError("Inavlid choice type '{}'".format(self.choice_type))

        type_validator(self.list_choices)

        # validate min-max selection value
        if self.min_selection is not None:
            if self.min_selection > len_choices:
                raise FieldDefinitionError("Minimum selection count {} cannot be greater than total choice count {}.".format(self.min_selection,len_choices))
        if self.min_selection is not None and self.max_selection is not None:
            validators.min_max_validator(self.min_selection,self.max_selection)

        # Validate if 'allow_other' is selected
        if self.allow_other:
            if self.other_value is None or self.other_text is None:
                raise FieldDefinitionError("Please set 'other_value' and 'other_text'.")
            else:
                # Check if 'list_choices' does not have 'other_value'
                if self.other_value in self.get_choice_keys():
                    raise FieldDefinitionError("Choice list cannot have '{}' since it is already used as 'Other' option.".format(self.other_value))

            # if self.other_option_type is None:
            #     raise FieldDefinitionError("Please select option type.")
            if self.other_question is None:
                raise FieldDefinitionError("Please enter the question to be asked when other is selected.")

    def get_choice_keys(self):
        return [ch.value for ch in self.list_choices]

    def iterate_choices(self):
        if self.choice_ordering == ChoiceOrder.ASCENDING:
            ordered_list_choices = sorted(self.list_choices, key = lambda ch: ch['value'])
        elif self.choice_ordering == ChoiceOrder.DESCENDING:
            ordered_list_choices = sorted(self.list_choices, key = lambda ch: ch['value'], reverse=True)
        elif self.choice_ordering == ChoiceOrder.RANDOM:
            ordered_list_choices = [ch for ch in self.list_choices]
            random.shuffle(ordered_list_choices)
        else:
            ordered_list_choices = self.list_choices

        return ordered_list_choices

    def get_all_choice_values(self):
        list_choices = [ch['value'] for ch in self.list_choices]
        if self.allow_other:
            list_choices.append(self.other_value)

        return list_choices


class RatingFormField(BasicFormField):
    """
    Defines a rating field that allows user to rate on a scale of 1 to 'max-score'.
    Rating is of type integer.

    **Authors**: Gagandeep Singh
    """
    choice_type = MCQ_Types.INT

    max_score = IntegerProperty(required=True, default=5, validators=[validators.validate_max_score])  # Maximum score
    widget = StringProperty(required=True, choices=FieldWidgets.choices_rating, default=FieldWidgets.RATING_STARS)

    def iterate_choices(self):
        return [{"value":i, "text":i} for i in range(1, (self.max_score+1))]

# ---------- /Fundamental FormFields ----------

# ---------- Methods ----------
def create_field_obj(field_dict):
    """
    Converts a field dictionary into a corresponding field object.

    :param condition_dict: dict
    :return: Field Object

    **Authors**: Gagandeep Singh
    """
    class_name = field_dict['_cls']
    try:
        field_obj = globals()[class_name](field_dict)
        return field_obj
    except:
        raise InvalidFormClass("'{}' is not a valid field class.".format(class_name))

