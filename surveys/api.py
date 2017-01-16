# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from tastypie import fields
from tastypie_mongoengine import resources
# from tastypie_mongoengine import fields
from datetime import datetime

from surveys.models import Survey, SurveyResponse
from utilities.tastypie_utils import GenericTastypieObject, SurveySessionAuthentication

class SurveyResponsesAPI(resources.MongoEngineResource):
    """
    An API resource to get summary of all responses for a survey.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        queryset = SurveyResponse.objects.all()
        # object_class = SurveyResponse

        resource_name = 'survey_responses'
        limit = 0
        max_limit = None
        allowed_methods = ('get',)
        filtering = {
            'survey_uid': ALL,
            'response_date' : ALL,
        }
        fields = ('id', 'survey_uid', 'phase_id', 'version_obsolete', 'user', 'response_uid', 'response_date', 'location', 'flags')
        authentication = SurveySessionAuthentication()

    def apply_filters(self, request, applicable_filters):
        # object_list_filtered = self._meta.queryset.filter(**applicable_filters)

        survey_uid = request.GET['survey_uid']
        if not Survey.objects.filter(survey_uid=survey_uid).exists():
            raise Exception("Invalid survey.")

        # Suspect
        is_suspect = request.GET.get('flags.suspect', None)
        if is_suspect is not None:
            applicable_filters['flags__suspect'] = bool(int(is_suspect))

        # object_list_filtered = object_list_filtered.filter(survey_uid=survey_uid).order_by('-created_on')
        # 'survey_uid__exact' filter is already in applicable_filters; so no need to add
        object_list_filtered = self._meta.queryset.filter(**applicable_filters).order_by('-created_on')

        return object_list_filtered

    def dehydrate(self, bundle):
        bundle.data["user"] = bundle.obj.user.to_mongo()
        bundle.data["location"] = bundle.obj.location.to_mongo()

        flags = bundle.obj.flags.to_mongo()
        suspect_reasons = []
        for s in flags['suspect_reasons']:
            suspect_reasons.append(s['text'])
        flags['suspect_reasons'] = suspect_reasons
        bundle.data["flags"] = flags

        return bundle

class SurveyResponseTrendAPI(Resource):
    """
    An API resource to display response submission trend of a survey.
    This is a custom api that aggregates responses on keys:
        ``response_date``, ``suspect``

    **Options**:

        - type: None = All responses; suspects = only suspects; non_suspects = only non suspects

    **Authors**: Gagandeep Singh
    """
    response_date   = fields.DateField(attribute='response_date')
    suspect         = fields.BooleanField(attribute='suspect')
    count           = fields.IntegerField(attribute='count')

    class Meta:
        object_class = GenericTastypieObject
        resource_name = 'survey_response_trend'
        allowed_methods = ('get',)
        limit=0
        max_limit=None

    def obj_get_list(self, bundle, **kwargs):
        # --- Obtain params and validate ---
        survey_uid = bundle.request.GET['survey_uid']
        trend_type = bundle.request.GET.get('type', None)

        survey = Survey.objects.get(survey_uid=survey_uid)   # Insures survey exists

        # --- Filters ---
        match = {
            "survey_uid": survey_uid
        }
        if trend_type:
            if trend_type == 'suspects':
                match['flags.suspect'] = True
            elif trend_type == 'non_suspects':
                match['flags.suspect'] = False
            else:
                raise Exception("Invalid trend type '{}'.".format(trend_type))
        # --- /Filters ---

        # --- Query ---
        result_aggr = SurveyResponse._get_collection().aggregate([
            { "$match" : match },
            {
                "$group" : {
                    "_id" : {
                        "dated" : { "$dateToString" : { "format" : "%Y-%m-%d", "date" : "$response_date" } },
                        "suspect" : "$flags.suspect"
                    },
                    "count" : {
                        "$sum" : 1
                    }
                }
            },
            {
                "$sort": { "_id.dated" : 1 }
            }
        ])

        data = []
        for row in result_aggr:
            obj = GenericTastypieObject()

            obj.response_date = datetime.strptime(row["_id"].get('dated'), '%Y-%m-%d').date()
            obj.suspect = row["_id"].get('suspect')
            obj.count = row['count']

            data.append(obj)

        return data