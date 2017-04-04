# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie_mongoengine import resources
from utilities.tastypie_utils import OrgConsoleSessionAuthentication, NoPaginator
import copy

from clients.models import Organization
from feedback.models import BspFeedbackForm, BspFeedbackResponse
from market.models import BusinessServicePoint

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

            # Get cache form attachment counts
            result_aggr = BusinessServicePoint._get_collection().aggregate([
                {
                    "$match": { "organization_id": org.id }
                },
                {
                    "$group":{
                        "_id": { "feedback_form_id": "$feedback_form_id" },
                        "count": { "$sum": 1 }
                    }
                }
            ])
            data_form_count = {}
            for row in result_aggr:
                data_form_count[row["_id"]["feedback_form_id"]] = row["count"]
            request.data_form_count = data_form_count


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

        bundle.data['attached_bsps'] = bundle.request.data_form_count.get(obj.id, None)

        return bundle


class BspFeedbackResponsesAPI(resources.MongoEngineResource):
    """
    An API resource to get summary of all bsp feedback responses.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = BspFeedbackResponse.objects.all()
        resource_name = 'bsp_feedback_responses'
        limit = 0
        max_limit = None
        allowed_methods = ('get',)
        filtering = {
            'bsp_id': ALL,
            'response_date' : ALL,
        }
        fields = ('id', 'version_obsolete', 'response_uid', 'response_date', 'flags')
        authentication = OrgConsoleSessionAuthentication(['market.businessservicepoint'])

    def apply_filters(self, request, applicable_filters):
        # object_list_filtered = self._meta.queryset.filter(**applicable_filters)

        # Caches
        request.cache_forms = {}
        request.cache_bsps = {}

        # --- Check BSP access ---
        # (a) Get all Bsp Ids
        filters_bsp = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
        if len(filters_bsp):
            list_bsp_ids = [ str(id) for id in BusinessServicePoint.objects.filter(**filters_bsp).values_list('id')]
        else:
            list_bsp_ids = None

        # (b) Check if bsp_id is to be filtered
        bsp_id = request.GET.get('bsp_id', None)
        if bsp_id:
            # Look in the list and add to main filters
            if list_bsp_ids is not None:
                if bsp_id in list_bsp_ids:
                    applicable_filters['bsp_id'] = bsp_id
                else:
                    # Not found; that is, does not have access
                    return []
            else:
                # Has access to all
                applicable_filters['bsp_id'] = bsp_id
        else:
            # BSP is not in filters; Add list of bsps in main filter if list is not empty
            if list_bsp_ids is not None:
                applicable_filters['bsp_id__in'] = list_bsp_ids
        # --- /Check BSP access ---

        # Suspect
        is_suspect = request.GET.get('flags.suspect', None)
        if is_suspect is not None:
            applicable_filters['flags__suspect'] = bool(int(is_suspect))

        object_list_filtered = self._meta.queryset.filter(**applicable_filters)

        return object_list_filtered.order_by('-response_date').only(*(self.Meta.fields+('bsp_id', 'form_id', 'user', 'location', 'rating_id', 'comment_id')))

    def dehydrate(self, bundle):
        bsp_id = bundle.obj.bsp_id
        bsp = bundle.request.cache_bsps.get(bsp_id, None)
        if bsp is None:
            bsp = bundle.obj.bsp
            bundle.request.cache_bsps[bsp_id] = bsp
        bundle.data['bsp'] = {
            'id': bsp_id,
            'name': bsp.name
        }

        form_id = bundle.obj.form_id
        form = bundle.request.cache_forms.get(form_id, None)
        if form is None:
            form = bundle.obj.form
            bundle.request.cache_forms[form_id] = form
        bundle.data['form'] = {
            'id': form_id,
            'title': form.title
        }

        bundle.data["user"] = bundle.obj.user.to_mongo()
        bundle.data["location"] = bundle.obj.location.to_mongo() if bundle.obj.location else {}

        flags = bundle.obj.flags.to_mongo()
        suspect_reasons = []
        for s in flags['suspect_reasons']:
            suspect_reasons.append(s['text'])
        flags['suspect_reasons'] = suspect_reasons
        bundle.data["flags"] = flags

        bundle.data['rating'] = bundle.obj.rating.rating
        bundle.data['comment'] = bundle.obj.comment.text if bundle.obj.comment_id else None

        return bundle