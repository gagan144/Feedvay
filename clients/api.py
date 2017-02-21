# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from django.db.models import Q

from clients.models import Organization, OrganizationMember
from utilities.tastypie_utils import OrgConsoleSessionAuthentication, NoPaginator

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


class OrganizationMembersAPI(ModelResource):
    """
    Tastypie resource to get all organization members.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = OrganizationMember.objects.all()
        resource_name = 'organization_members'
        limit = 0
        max_limit = None
        list_allowed_methods = ['get']
        authentication = OrgConsoleSessionAuthentication(['clients.organizationmember'])
        paginator_class = NoPaginator

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(self.__class__, self).apply_filters(request, applicable_filters)

        reg_user = request.user.registereduser
        org_uid = request.GET['c']
        org = Organization.objects.get(org_uid=org_uid)

        filters = request.permissions['clients.organizationmember']['data_access']
        if filters is None:
            return []
        else:
            filters['organization__org_uid'] = org_uid
            filters['deleted'] = False

            base_object_list = base_object_list.filter(**filters)

        return base_object_list.exclude(registered_user_id=reg_user.id).select_related('registered_user', 'registered_user__user', 'created_by')

    def dehydrate(self, bundle):
        obj = bundle.obj

        bundle.data['registered_user'] = {
            'id': obj.registered_user.id,
            'username': obj.registered_user.user.username,
            'first_name': obj.registered_user.user.first_name,
            'last_name': obj.registered_user.user.last_name,
            'email': obj.registered_user.user.email,
        }

        bundle.data['created_by'] = {
            'id': obj.created_by.id,
            'username': obj.created_by.username,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
        }

        bundle.data['roles'] = list(obj.registered_user.roles.all().values('id', 'name'))
        bundle.data['is_superuser'] = obj.registered_user.superuser_in.filter(id=obj.organization.id).exists()

        return bundle