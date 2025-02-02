# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django import template
import ujson
from django.contrib.auth.models import User

from accounts.utils import lookup_permission

register = template.Library()

@register.filter
def jsonify(obj, encoding=True):
    """
    Django template filter to obtain json string.

    :param obj: JSON object
    :return: JSON string

    **Authors**: Gagandeep Singh
    """
    if encoding:
        return ujson.dumps(obj, ensure_ascii=False).encode('utf8')
    else:
        return ujson.dumps(obj, ensure_ascii=False)

@register.filter
def get_item(dictionary, key):
    """
    Django template tag to get value for a key in a dictionary.

    :param dictionary: Dictionary object
    :param key: Key to lookup
    :return: Value for the key. None if key is not found.

    **Authors**: Gagandeep Singh
    """
    return dictionary.get(key)

@register.filter
def get_user_readable(user_id, display_format):
    """
    Django templatetag that converts user id into readable user name.

    :param user_id: :class:`django.contrib.auth.models.User` instance id
    :param display_format: Display format: \*, username, full_name, first_name
    :return: Display string

    **Authors**: Gagandeep Singh
    """
    s = ''
    try:
        user = User.objects.get(id=user_id)

        if display_format == 'full_name':
            s = "{} {}".format(user.first_name, user.last_name)
        elif display_format == 'username':
            s = user.username
        elif display_format == 'first_name':
            s = user.first_name
        elif display_format == '*':
            s = '{} {} ({})'.format(user.first_name, user.last_name, user.username)
    except User.DoesNotExist:
        pass

    return s

@register.filter
def get_python_type(obj, format_type):
    """
    Returns python type of the object.
    :param obj: Object
    :param format_type: None- Python class, 'name'- string name
    :return: Python type

    **Authors**: Gagandeep Singh
    """
    t = type(obj)

    return t if format_type is None else t.__name__

@register.filter
def multiply(value, multiplier):
    """
    Returns multiplication value and multiplier.
    :param value: Value
    :param multiplier: None- Python class, 'name'- string name
    :return: value*multiplier

    **Authors**: Gagandeep Singh
    """
    return value*multiplier

@register.filter
def has_permission(perm_json, perm_key):
    """
    Method to tell if perm_json has permission or not.
    This method uses ``accounts.utils.lookup_permission()`` method.

    :param perm_json: Permission JSON
    :param perm_key: ``.`` separated permission key of format ``<app-label>.<model-name>.<perm-codename>``
    :return: True if json has permission else false

    **Authors**: Gagandeep Singh
    """
    return lookup_permission(perm_json, perm_key)

@register.filter
def range_loop(max_val, step=1):
    """
    Method to return integer loop range from 1 to given max value.

    :param max_val: Range max value (including)
    :param step: (Default: 1) Steps for looping
    :return: range(1, max_value+step, step)
    """
    return range(1, max_val+step, step)