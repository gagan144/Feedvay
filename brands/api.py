# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from django.db.models import Q

from brands.models import Brand, BrandChangeRequest
from utilities.tastypie_utils import BrandConsoleSessionAuthentication, NoPaginator

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
        paginator_class = NoPaginator

    def obj_get_list(self, bundle, **kwargs):
        queryset = self._meta.queryset
        q = bundle.request.GET['q']

        return queryset.filter(Q(name__icontains=q)|Q(slug__icontains=q))


class BrandChangeRequestAPI(ModelResource):
    """
    Tastypie resource to get all change request for a brand.

    .. warning::
        This resource is only applicable for **brand console**.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    class Meta:
        queryset = BrandChangeRequest.objects.all().only('id', 'brand', 'registered_user', 'status', 'remarks', 'created_on', 'modified_on')
        resource_name = 'brand_change_requests'
        limit = 20
        max_limit = None
        fields = ('id', 'brand', 'registered_user', 'status', 'remarks', 'created_on', 'modified_on')
        list_allowed_methods = ['get']
        authentication = BrandConsoleSessionAuthentication() #SessionAuthentication()

    def apply_filters(self, request, applicable_filters):
        object_list_filtered = self._meta.queryset.filter(**applicable_filters)

        brand = request.curr_brand
        object_list_filtered = object_list_filtered.filter(brand=brand).select_related('registered_user').order_by('-created_on')

        return object_list_filtered

    # def obj_get_list(self, bundle, **kwargs):
    #     # try:
    #     brand = bundle.request.curr_brand
    #
    #     queryset = self._meta.queryset
    #     return queryset.filter(brand=brand).select_related('registered_user').order_by('-created_on')
    #     # except AttributeError:
    #     #     raise Exception("Unauthorized access.")

    def dehydrate(self, bundle):
        obj = bundle.obj
        bundle.data['brand_id'] = obj.brand_id
        bundle.data['registered_user'] = {
            "id": obj.registered_user_id,
            "full_name": "{} {}".format(obj.registered_user.user.first_name, obj.registered_user.user.last_name)
        }

        return bundle.data