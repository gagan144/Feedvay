# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from tastypie import fields
from django.db.models import Q
from mongoengine.fields import EmbeddedDocumentListField
from operator import itemgetter

from market.models import Brand, get_bsp_labels
from utilities.tastypie_utils import NoPaginator, GenericTastypieObject

class BrandExistenceAPI(ModelResource):
    """
    Tastypie resource to get any existing brand for given query text. This resource is mostly
    used while creating/editing a brand inside console.

    .. warning::
        This resource is not meant to list brands or to be used for public search.

    **Type**: GET

    **Points**:

        - All brands excluding with status ``deleted`` are returned.
        - Maximum of 10 records are returned for given query.
        - Only limited information about the brand is returned.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = Brand.objects.all().only('id', 'organization', 'brand_uid', 'name', 'slug')
        resource_name = 'search_existence'
        limit = 0
        max_limit = 10
        fields = ('id', 'organization', 'brand_uid', 'name', 'slug')
        list_allowed_methods = ['get']
        authentication = SessionAuthentication()
        paginator_class = NoPaginator

    def obj_get_list(self, bundle, **kwargs):
        queryset = self._meta.queryset
        q = bundle.request.GET['q']

        return queryset.filter(Q(name__icontains=q)|Q(slug__icontains=q))

class BspLabelsAPI(Resource):
    """
    Tastypie resource to get a BSP type labels.

    **Type**: GET

    **Points**:

        - Param ``type`` specifies BSP type
        - Param ``include_common`` (0,1) can be used include or exclude common bsp labels. By default, these are included.

    **Authors**: Gagandeep Singh
    """
    label       = fields.CharField(attribute='label', help_text='Label/identified iof the attribute.')
    description = fields.CharField(attribute='description', null=True, help_text='Description of the attribute.')
    dtype       = fields.CharField(attribute='dtype', help_text='Data type of the attribute')
    required    = fields.BooleanField(attribute='required', help_text='Whether this field is mandatory or not.')
    path        = fields.CharField(attribute='path', help_text='Dot (.) separated path in the model.')

    class Meta:
        object_class = GenericTastypieObject
        resource_name = 'bsp_type_labels'
        allowed_methods = ('get',)
        limit=0
        max_limit=None
        include_resource_uri = False
        authentication = SessionAuthentication()

    def obj_get_list(self, bundle, **kwargs):
        bsp_type_code = bundle.request.GET['type']
        include_common = int(bundle.request.GET.get('include_common', 1))

        data = []
        for attr in get_bsp_labels(bsp_type_code):
            if (attr['is_common']==True and include_common) or attr['is_common']==False:
                obj = GenericTastypieObject()
                obj.label = attr['label']
                obj.description = attr['description']
                obj.dtype = attr['dtype']
                obj.required = attr['required']
                obj.path = attr['path']

                data.append(obj)

        return data
