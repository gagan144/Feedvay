# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django import template
import ujson

register = template.Library()

@register.filter
def jsonify(obj):
    return ujson.dumps(obj, ensure_ascii=False).encode('utf8')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)