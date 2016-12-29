# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import SessionAuthentication
from tastypie_mongoengine import resources
from tastypie_mongoengine import fields
from datetime import datetime

from surveys.models import Survey, SurveyResponse

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
        authentication = SessionAuthentication()    #TODO: Survey access authentication

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
