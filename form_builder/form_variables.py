# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from jsonobject import *
from jsonobject.base_properties import DefaultProperty
import validators
from form_exceptions import VariableDefinitionError, FieldDefinitionError, InvalidConstantSchema, InvalidCalculatedFieldSchema
from form_builder.utils import JsCompilerTool
from languages.models import Translation

class Constant(JsonObject):
    """
    Defines a readonly constant in the form whose value can be used to conditionally
    change form behavior.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    label           = StringProperty(required=True, validators=[validators.validate_label])
    text_ref        = StringProperty()      # Text for reference use only
    text_translation_id = StringProperty()  # Raw id of text translation ('languages.Translation')
    value           = DefaultProperty(required=True)
    show_on_form    = BooleanProperty(required=True, default=False)
    include_in_answers = BooleanProperty(required=True, default=False)     # Include this field in answers part of the form

    @property
    def translation(self):
        return Translation.objects.with_id(self.text_translation_id) if self.text_translation_id else None

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.label)

    def __init__(self, _obj=None, **kwargs):
        super(Constant, self).__init__(_obj=_obj, **kwargs)

        if self.show_on_form:
            if self.text_translation_id is None:
                raise VariableDefinitionError("Text translation required for this constant since 'show_on_form' is true.")

    def to_json(self):
        if self.text_translation_id:
            self.text_ref = self.translation.sentence
        return super(Constant, self).to_json()

class CalculatedField(JsonObject):
    """
    Defines a calculated field whose value is the resultant of the expression.
    This field is different from any 'BasicFormField'.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    label           = StringProperty(required=True, validators=[validators.validate_label])
    text_ref        = StringProperty()      # Text for reference use only
    text_translation_id = StringProperty()  # Raw id of text translation ('languages.Translation')
    expression      = StringProperty(required=True, validators=[validators.validate_calc_fld_expression])  # Cannot contain any other calculated field
    show_on_form    = BooleanProperty(required=True, default=False)
    include_in_answers = BooleanProperty(required=True, default=False)     # Include this field in answers part of the form

    @property
    def translation(self):
        return Translation.objects.with_id(self.text_translation_id) if self.text_translation_id else None

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.label)

    def __init__(self, _obj=None, **kwargs):
        super(CalculatedField, self).__init__(_obj=_obj, **kwargs)

        if self.show_on_form:
            if self.text_translation_id is None:
                raise FieldDefinitionError("Text translation required for this calculated field since 'show_on_form' is true.")


    def get_expression_variables(self):
        jscompiler = JsCompilerTool(self.expression)
        return jscompiler.extract_variables()

    def to_json(self):
        if self.text_translation_id:
            self.text_ref = self.translation.sentence
        return super(CalculatedField, self).to_json()

# ---------- Methods ----------
def create_constant_obj(constant_dict):
    """
    Converts a constant dictionary into a corresponding constant object.

    :param constant_dict: dict
    :return: Constant Object

    **Authors**: Gagandeep Singh
    """
    try:
        constant_obj = Constant(constant_dict)
        return constant_obj
    except:
        raise InvalidConstantSchema("Unable to create Constant object, invalid dict.")


def create_calculated_field_obj(calc_fld_dict):
    '''
    Converts a calculated field dictionary into a corresponding CalculatedField object.
    :param calc_fld_dict: dict
    :return: CalculatedField Object
    '''
    try:
        calc_fld_obj = CalculatedField(calc_fld_dict)
        return calc_fld_obj
    except:
        raise InvalidCalculatedFieldSchema("Unable to create CalculatedField object, invalid dict.")