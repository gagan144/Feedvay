# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

import re
from form_builder.form_exceptions import *
from form_builder.utils import JsCompilerTool

# ---------- General use validations ----------
def validate_label(label):
    # if re.match(r'.*[ \\\#\%\$\^\*\@\!\-\(\)\:\;\'\"\{\}\[\]].*', label) is None and not label.__contains__('__'):
    # if re.match(r'.*[ \\\#\%\$\^\*\@\!\-\:\;\'\"\/\>\<\~\`\)\(\}\{\]\[\|\+].*', label) is None and not label.__contains__('__'):
    if re.match('^[A-Za-z0-9_]+$',label) is not None and not label.__contains__('__'):
        pass
    else:
        raise FieldDefinitionError("Label '{}' cannot contain special characters, space or double underscore.".format(label))

def validate_no_special_char(value):
    if re.match('^[A-Za-z0-9]+$', value) is None:
        raise FieldValueError("Value cannot have special characters.")

def validate_email(email_addr):
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_addr)
    if match is None:
        raise FieldValueError("Invalid email '{}'.".format(email_addr))

# ---------- Multiple Choices validation ----------
def int_choices(list_choices):
    """
    Validate if 'value' in all choices are of type int or not.
    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]
    """

    for ch in list_choices:
        if not isinstance(ch.value,int):
            raise FieldDefinitionError("Choice value '{}' is not an integer.".format(str(ch.value)))


def float_choices(list_choices):
    """
    Validate if 'value' in all choices are of type int or not.
    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]
    """

    for ch in list_choices:
        if not isinstance(ch.value,float):
            raise FieldDefinitionError("Choice value '{}' is not a decimal.".format(str(ch.value)))


def string_choices(list_choices):
    """
    Validate if 'value' in all choices are of type string or not.
    :param list_choice: [ <fields.Choice>, <fields.Choice>, ... ]
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
    :param min_val:
    :param max_val:
    :return:
    """
    if min_val > max_val:
        raise AssertionError("Minimum value {} cannot be greater than maximum value {}.".format(min_val, max_val))

# ---------- Rating ----------
def validate_max_score(max_score):
        if not (3 <= max_score <= 12):
            raise FieldDefinitionError("Max Score must be between 3 and 12.")

# ---------- Calculated Field Validators ----------
def validate_calc_fld_expression(expression):
    jscompiler = JsCompilerTool(expression)
    list_var = jscompiler.extract_variables()

    for absolute_var in list_var:
        if absolute_var.__contains__("calculated_fields."):
            varname = absolute_var.replace("$scope.calculated_fields.", "")
            raise InvalidCalculatedFieldExpression("Calculated field expression cannot use another calculated field '{}'.".format(varname))

