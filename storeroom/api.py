# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie_mongoengine import resources

from django.contrib.auth.models import User

from clients.models import Organization
from storeroom.models import DataRecord
from utilities.tastypie_utils import OrgConsoleSessionAuthentication, NoPaginator

class DataRecordOrgAPI(resources.MongoEngineResource):
    """
    An API resource to get all data records in storeroom for an organization.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = DataRecord.objects.all()
        resource_name = 'data_records_org'
        limit = 0
        max_limit = None
        allowed_methods = ('get',)
        filtering = {
            'context': ALL,
            'batch_id' : ALL,
        }
        excludes = ('data', 'modified_on')
        authentication = OrgConsoleSessionAuthentication(['market.businessservicepoint.add_businessservicepoint'])

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(self.__class__, self).apply_filters(request, applicable_filters)

        org_uid = request.GET['c']
        org = Organization.objects.get(org_uid=org_uid)

        base_object_list = base_object_list.filter(organization_id=org.id)

        request.cache_users = {}

        return base_object_list.exclude('modified_on')

    def dehydrate(self, bundle):
        obj = bundle.obj

        data_json = obj.data_json
        bundle.data['data'] = {
            'name': data_json.get('name', None)
        }

        user = bundle.request.cache_users.get(obj.created_by, None)
        if user is None:
            user = User.objects.get(id=obj.created_by)
            bundle.request.cache_users[user.id] = user

        bundle.data['created_by'] = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        return bundle