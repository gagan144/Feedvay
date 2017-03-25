# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from utilities.tastypie_utils import OrgConsoleSessionAuthentication, NoPaginator
import copy

from clients.models import Organization
from feedback.models import BspFeedbackForm, BspFeedbackAssociation

class BspFeedbackFormsAPI(ModelResource):
    """
    Tastypie resource to get all BSP feedback questionnaire ofan organization

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = BspFeedbackForm.objects.all()
        resource_name = 'bsp_feedback_forms'
        limit = 0
        max_limit = None
        list_allowed_methods = ['get']
        fields = ('id', 'title', 'user_notes', 'is_ready', 'created_on', 'created_by', 'updated_on')
        authentication = OrgConsoleSessionAuthentication(['feedback.bspfeedbackform'])

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(self.__class__, self).apply_filters(request, applicable_filters)

        org_uid = request.GET['c']
        org = Organization.objects.get(org_uid=org_uid)

        filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
        if filters is None:
            return []
        else:
            filters['organization_id'] = org.id

            base_object_list = base_object_list.filter(**filters)
            return base_object_list.select_related('created_by').only(*self.Meta.fields)

    def dehydrate(self, bundle):
        obj = bundle.obj

        bundle.data['created_by'] = {
            'id': obj.created_by.id,
            'username': obj.created_by.username,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
        }

        bundle.data['attached_bsps'] = BspFeedbackAssociation.objects.filter(form_id=obj.id).count()

        return bundle
