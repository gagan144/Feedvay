# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import template

import json

register = template.Library()

@register.filter
def get_translation_text(translation, lang_code=None):
    """
    Django templatetags to retrieve translation text for a language code from a given translation.

    :param translation: Instance of :class:`languages.models.Translation`
    :param lang_code: Language code
    :return: Unicode language text

    **Authors**: Gagandeep Singh
    """
    if lang_code:
        return translation.translations.get(lang_code)
    else:
        return translation.sentence

@register.filter
def to_js_json_unicode(trans_json):
    """
    Django template tag to obtain javascript json for a :class:`languages.models.Translation` instance.

    :param trans_json: Translation python JSON object
    :return: Javascript JSON object.

    **Authors**: Gagandeep Singh
    """
    return json.dumps(trans_json, ensure_ascii=False).encode('utf8')