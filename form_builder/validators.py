# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

import re
from form_builder.form_exceptions import *
from form_builder.utils import JsCompilerTool

# ---------- General use validations ----------
def validate_label(label):
    """
    Method to validate if the label name follows conventions for declaring a javascript variable.

    :param label: Label name

    **Throws**: :class:`form_builder.form_exceptions.FieldDefinitionError`

    **Authors**: Gagandeep Singh
    """
    # if re.match(r'.*[ \\\#\%\$\^\*\@\!\-\(\)\:\;\'\"\{\}\[\]].*', label) is None and not label.__contains__('__'):
    # if re.match(r'.*[ \\\#\%\$\^\*\@\!\-\:\;\'\"\/\>\<\~\`\)\(\}\{\]\[\|\+].*', label) is None and not label.__contains__('__'):
    if re.match('^[A-Za-z0-9_]+$',label) is not None and not label.__contains__('__'):
        pass
    else:
        raise FieldDefinitionError("Label '{}' cannot contain special characters, space or double underscore.".format(label))

def validate_no_special_char(value):
    """
    Method to check that value must not contain any special characters.

    :param value: Value

    **Throws**: :class:`form_builder.form_exceptions.FieldValueError`

    **Authors**: Gagandeep Singh
    """
    if re.match('^[A-Za-z0-9]+$', value) is None:
        raise FieldValueError("Value cannot have special characters.")

def validate_email(email_addr):
    """
    Method to validate email address.

    :param email_addr: Email address

    **Throws**: :class:`form_builder.form_exceptions.FieldValueError`

    **Authors**: Gagandeep Singh
    """
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_addr)
    if match is None:
        raise FieldValueError("Invalid email '{}'.".format(email_addr))

# ---------- Multiple Choices validation ----------
def int_choices(list_choices):
    """
    Validate if 'value' in all choices are of type int or not.

    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]

    **Throws**: :class:`form_builder.form_exceptions.FieldDefinitionError`

    **Authors**: Gagandeep Singh
    """

    for ch in list_choices:
        if not isinstance(ch.value,int):
            raise FieldDefinitionError("Choice value '{}' is not an integer.".format(str(ch.value)))


def float_choices(list_choices):
    """
    Validate if 'value' in all choices are of type int or not.

    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]

    **Throws**: :class:`form_builder.form_exceptions.FieldDefinitionError`

    **Authors**: Gagandeep Singh
    """

    for ch in list_choices:
        if not isinstance(ch.value,float):
            raise FieldDefinitionError("Choice value '{}' is not a decimal.".format(str(ch.value)))


def string_choices(list_choices):
    """
    Validate if 'value' in all choices are of type string or not.

    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]

    **Throws**: :class:`form_builder.form_exceptions.FieldDefinitionError`

    **Authors**: Gagandeep Singh
    """

    for ch in list_choices:
        if not ( isinstance(ch.value,str) or isinstance(ch.value, unicode)):
                raise FieldDefinitionError("Choice value '{}' is not a string.".format(str(ch.value)))

# def validate_choice(ch_value):
#     if re.match('^[A-Za-z0-9_ ]+$',ch_value) is None:
#         raise FieldDefinitionError("Choice value '{}' cannot contain any special characters. Only underscore & spaces allowed.".format(ch_value))

# ---------- Integer/Range Validations ----------
def min_max_validator(min_val, max_val):
    """
    Validates if 'min_val' <= 'max_val'
    :param min_val: Test value which is supposed to be smaler.
    :param max_val: Test value which is supposed to be greater.

    **Throws**: AssertionError

    **Authors**: Gagandeep Singh
    """
    if min_val > max_val:
        raise AssertionError("Minimum value {} cannot be greater than maximum value {}.".format(min_val, max_val))

# ---------- Rating ----------
def validate_max_score(max_score):
    """
    Method to check if max score is between 3 and 12 for a rating field.

    :param max_score: Max score

    **Throws**: :class:`form_builder.form_exceptions.FieldDefinitionError`

    **Authors**: Gagandeep Singh
    """
    if not (3 <= max_score <= 12):
        raise FieldDefinitionError("Max Score must be between 3 and 12.")

# ---------- Calculated Field Validators ----------
def validate_calc_fld_expression(expression):
    """
    Validates calculated field evaluation expression.

    :param expression: Expression

    **Throws**: :class:`form_builder.form_exceptions.InvalidCalculatedFieldExpression`

    **Authors**: Gagandeep Singh
    """
    jscompiler = JsCompilerTool(expression)
    list_var = jscompiler.extract_variables()

    for absolute_var in list_var:
        if absolute_var.__contains__("calculated_fields."):
            varname = absolute_var.replace("$scope.calculated_fields.", "")
            raise InvalidCalculatedFieldExpression("Calculated field expression cannot use another calculated field '{}'.".format(varname))

