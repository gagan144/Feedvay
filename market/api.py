# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from tastypie import fields
from django.db.models import Q

from market.models import Brand, BusinessServicePoint
from market.bsp_types import *
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
    label       = fields.CharField(attribute='label')
    description = fields.CharField(attribute='description', null=True)

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
        if include_common:
            for lbl, fld in BusinessServicePoint._fields.iteritems():
                obj = GenericTastypieObject()
                obj.label = lbl
                try:
                    obj.description = fld.help_text
                except AttributeError:
                    obj.description = None

                data.append(obj)

        # AS per BSP type
        type_class = MAPPING_BSP_CLASS[bsp_type_code]
        for lbl, fld in type_class.properties().iteritems():
            obj = GenericTastypieObject()
            obj.label = lbl
            obj.description = lbl

            data.append(obj)

        return data
