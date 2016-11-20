# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from django.db.models import Q

from brands.models import Brand

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
        queryset = Brand.objects.exclude(status=Brand.ST_DELETED).only('id', 'brand_uid', 'name', 'acronym', 'slug')
        resource_name = 'search_existence'
        limit = 0
        max_limit = 10
        fields = ('id', 'brand_uid', 'name', 'acronym', 'slug')
        list_allowed_methods = ['get']
        authentication = SessionAuthentication()

    def obj_get_list(self, bundle, **kwargs):
        queryset = self._meta.queryset
        q = bundle.request.GET['q']

        return queryset.filter(Q(name__icontains=q)|Q(slug__icontains=q))