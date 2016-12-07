# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django import template
import ujson

register = template.Library()

@register.filter
def jsonify(obj):
    """
    Django template filter to obtain json string.

    :param obj: JSON object
    :return: JSON string

    **Authors**: Gagandeep Singh
    """
    return ujson.dumps(obj, ensure_ascii=False).encode('utf8')

@register.filter
def get_item(dictionary, key):
    """
    Djago template tag to get value for a key in a dictionary.

    :param dictionary: Dictionary object
    :param key: Key to lookup
    :return: Value for the key. None if key is not found.

    **Authors**: Gagandeep Singh
    """
    return dictionary.get(key)