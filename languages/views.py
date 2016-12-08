# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.http.response import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

# from form_builder.models import Form
from languages.models import *
from utilities.decorators import minified_response
from utilities.api_utils import ApiResponse

import ujson

from form_builder.models import Form

@minified_response
def form_translations(request, form_id):
    """
    A view to server translation javascript file for a form.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    form = Form.objects.get(id=form_id)
    NM_IMPLICIT = "IMPLICIT"

    set_languages = set()
    list_translations = []
    list_translations += form.get_translations()
    list_translations += Translation.objects.filter(always_include_in_form=True)

    # Create language set
    translations = {
        "eng" : {
            NM_IMPLICIT: {}
        }
    }

    for trans_obj in list_translations:
        id = str(trans_obj.unique_id)

        # Add default english
        if trans_obj.always_include_in_form:
            translations["eng"][NM_IMPLICIT][trans_obj.unique_id] = trans_obj.sentence
        else:
            translations["eng"][id] = trans_obj.sentence

        # Loop over other languages and add them
        for lang_code, text in trans_obj.translations.iteritems():
            lang_code = str(lang_code)
            if not translations.has_key(lang_code):
                translations[lang_code] = {
                    NM_IMPLICIT: {}
                }

            if trans_obj.always_include_in_form:
                translations[lang_code][NM_IMPLICIT][trans_obj.unique_id] = text
            else:
                translations[lang_code][id] = text

    data = {
        "translations": translations
    }

    return render_to_response('languages/translations_js.html', data, content_type="application/javascript; charset=utf-8")

# # ==================== Staff admin ====================
# @login_required
# def save_translation(request):
#     """
#     A view that accepts POST data for new or existing translation and save it to model
#     database.
#     """
#     if request.method.lower() == 'post':
#         data = ujson.loads(request.POST['data'])
#         if data.get("id", None):
#             # Existing translation
#             translation = Translation.objects.get(pk=data["id"])
#         else:
#             # New Translation
#             translation = Translation()
#
#         # Copy data
#         unique_id = data.get("unique_id", None)
#         if unique_id is None or unique_id == '':
#             unique_id = None
#
#         translation.unique_id = unique_id
#         translation.is_paragraph = data.get("is_paragraph", False)
#         translation.sentence = data["sentence"]
#         translation.translations = data["translations"]
#         translation.tags = data.get("tags",None)
#         translation.is_public = data.get("is_public", False)
#         translation.always_include_in_form = data.get("always_include_in_form", False)
#         translation.save()
#
#         api_response = ApiResponse(status=ApiResponse.ST_SUCCESS, message="Ok")
#         api_response.add("translation_id", str(translation.pk))
#         return api_response.gen_http_response()
#     else:
#         return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()
#
# # ==================== /Staff admin ====================