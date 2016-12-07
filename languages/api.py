# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie_mongoengine import resources
from django.template.defaultfilters import striptags

from languages.models import Translation
from utilities.tastypie_utils import StaffSessionAuthentication

# class TranslationsAPI(resources.MongoEngineResource):
#     """
#     API for admin user to list all translations in the database.
#
#     **Points**:
#
#         - Only **staff user** or **superuser** is allowed to access this resource.
#
#     **Authors**: Gagandeep Singh
#     """
#     class Meta:
#         queryset = Translation.objects.all()
#         resource_name = 'translations'
#         limit = 0
#         max_limit = None
#         filtering = {
#             'sentence': ALL,
#             'always_include_in_form' : ALL,
#             'created_on' : ALL,
#         }
#         excludes = ('translations',)
#         authentication = StaffSessionAuthentication() #SessionAuthentication()
#
#     def dehydrate(self, bundle):
#         if bundle.obj.is_paragraph:
#             bundle.data["sentence"] = striptags(bundle.obj.sentence[:50])[:20] + " ..."
#         return bundle

class TranslationSearchAPI(resources.MongoEngineResource):
    """
    An API for user to search for publicly available translations and use them in the form.
    Only those translations which are publicly allowed and are not paragraph are accessible.

    **Points**:

        - Any logged user can access this resource.


    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = Translation.objects.filter(is_public=True, is_paragraph__ne=True)
        resource_name = 'translation_search'
        limit = 7
        max_limit = 10
        fields = ('id', 'unique_id', 'sentence', 'translations', 'list_language_codes')
        authentication = SessionAuthentication()

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(self.__class__, self).apply_filters(request, applicable_filters)

        q_text = request.GET['q']
        base_object_list = base_object_list.search_text(q_text)

        return base_object_list