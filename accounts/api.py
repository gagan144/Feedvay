# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
import copy

from clients.models import Organization
from accounts.models import OrganizationRole
from utilities.tastypie_utils import NoPaginator, OrgConsoleSessionAuthentication

class OrganizationRolesAPI(ModelResource):
    """
    Tastypie resource to get all organization roles.
    This resources applies permissions & data access before querying model.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = OrganizationRole.objects.all()
        resource_name = 'organization_roles'
        limit = 0
        max_limit = None
        list_allowed_methods = ['get']
        authentication = OrgConsoleSessionAuthentication(['accounts.organizationrole'])
        paginator_class = NoPaginator

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(self.__class__, self).apply_filters(request, applicable_filters)

        org_uid = request.GET['c']
        org = Organization.objects.get(org_uid=org_uid)

        filter_org = copy.deepcopy(request.permissions['accounts.organizationrole']['data_access'])
        if filter_org is None:
            return []
        else:
            filter_org['organization__org_uid'] = org_uid
            base_object_list = base_object_list.filter(**filter_org)
            return base_object_list.select_related('created_by')

    def dehydrate(self, bundle):
        obj = bundle.obj

        bundle.data['count_permissions'] = obj.permissions.all().count()
        bundle.data['created_by'] = {
            'id': obj.created_by.id,
            'username': obj.created_by.username,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
        }

        return bundle
