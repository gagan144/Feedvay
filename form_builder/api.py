# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from utilities.tastypie_utils import StaffSessionAuthentication

from form_builder.models import Form

# class FormsAPI(ModelResource):
#     """
#     API resource to list all forms. For staff admin only.
#
#     **Authors**: Gagandeep Singh
#     """
#     class Meta:
#         queryset = Form.objects.all()
#         resource_name = 'forms'
#         limit = 0
#         max_limit = None
#         filtering = {
#             'title': ALL,
#             'created_on' : ALL,
#         }
#         fields = ('id', 'title', 'theme_skin', 'languages', 'version', 'created_on', 'updated_on')
#         authentication = StaffSessionAuthentication() #SessionAuthentication()
#
#     def dehydrate(self, bundle):
#         obj = bundle.obj
#
#         # Theme
#         skin = obj.theme_skin
#         bundle.data['theme'] = {
#             "full_name": str(skin),
#             "skin_name": skin.name,
#             "theme_name": skin.theme.name
#         }
#
#         # Languages
#         bundle.data['languages'] = list(obj.languages.all().values_list('name', flat=True))
#
#         return bundle