# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from django.db.models import Q

from clients.models import Organization
from utilities.tastypie_utils import NoPaginator

class OrgExistenceAPI(ModelResource):
    """
    Tastypie resource to get any existing organization for given query text. This resource is mostly
    used while creating/editing an organization inside console.

    .. note::
        This resource is not meant to list organizations or to be used for public search.

    **Type**: GET

    **Points**:

        - All organizations excluding with status ``deleted`` are returned.
        - Maximum of 10 records are returned for given query.
        - Only limited information about the organization is returned.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = Organization.objects.exclude(status=Organization.ST_DELETED).only('id', 'org_uid', 'name', 'acronym', 'slug')
        resource_name = 'search_existence'
        limit = 0
        max_limit = 10
        fields = ('id', 'org_uid', 'name', 'acronym', 'slug')
        list_allowed_methods = ['get']
        authentication = SessionAuthentication()
        paginator_class = NoPaginator

    def obj_get_list(self, bundle, **kwargs):
        queryset = self._meta.queryset
        q = bundle.request.GET['q']

        return queryset.filter(Q(name__icontains=q)|Q(slug__icontains=q))