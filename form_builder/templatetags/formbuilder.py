# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django import template
from importlib import import_module

from form_builder import fields
from form_builder import layouts
from form_builder import conditions

register = template.Library()

@register.filter
def is_field(node):
    """
    Method to check if component is a form field.

    :param node: component
    :return: bool

    **Authors**: Gagandeep Singh
    """
    return True if isinstance(node, fields.BasicFormField) else False

@register.filter
def is_layout(node):
    """
    Method to check if component is a form layout.

    :param node: component
    :return: bool

    **Authors**: Gagandeep Singh
    """
    return True if isinstance(node, layouts.BaseLayout) else False

@register.filter
def is_condition(node):
    """
    Method to check if component is a form condition.

    :param node: component
    :return: bool

    **Authors**: Gagandeep Singh
    """
    return True if isinstance(node, conditions.BaseCondition) else False

@register.filter
def is_instance(value, class_str):
    """
    Check if object is instance of given class.

    **Authors**: Gagandeep Singh
    :param value: Object value
    :param class_str: Class name
    :return: bool

    **Authors**: Gagandeep Singh
    """
    split = class_str.split('.')
    # return isinstance(value, getattr(import_module('.'.join(split[:-1])), split[-1]))
    return isinstance(value, getattr(import_module('.'+'.'.join(split[:-1]), package='form_builder'), split[-1]))

@register.filter
def as_js_variable(value, type):
    """
    Method to return value as javascript variable.

    :param value: Python value
    :param type: Type
    :return: Javascript value

    **Authors**: Gagandeep Singh
    """
    if type == fields.DataType.STRING:
        return "'{}'".format(value)
    else:
        return value

@register.filter
def as_js_variable_auto(value):
    """
    Method to automatically detect and convert python value to javascript value.

    :param value: Python value
    :return: Javascript value

    **Authors**: Gagandeep Singh
    """
    if isinstance(value, str) or isinstance(value, unicode):
        return "'{}'".format(value)
    else:
        return value

@register.filter
def get_trans_from_lookup(lookup_dict, id):
    """
    Method to lookup translatio from translation dictionary.

    :param lookup_dict: Lookup translation dict
    :param id: Key
    :return: Translation

    **Authors**: Gagandeep Singh
    """
    trans = lookup_dict[id]
    return trans


