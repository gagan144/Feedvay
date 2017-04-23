# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.http import HttpResponseForbidden
from django.shortcuts import Http404
import copy

from surveys.models import Survey
from utilities.api_utils import ApiResponse


def survey_access_check(exception_type='response'):
    """
    Django view decorator to check if user has access permission for a survey or not.

    :param exception_type: Type of forbidden response:
        ``response``: 403 page with message,
        ``api``: Forbidden response as per :class:`utilities.api_utils.ApiResponse`.

    It assumes that:

        - Registered User has been cjecked for credentials.
        - User has ``surveys.survey`` permission.

    All views using this decorator are expected to receive ``survey_uid`` in one of the following ways:

        - In url regex. Example: ``/path/to/survey/<survey_uid>/``
        - In GET parameters: ``/path/to/survey/?survey_uid=<survey_uid>``
        - In POST parameters: ``survey_uid=<survey_uid>``

        The order of evaluation is the same as listed and if survey_uid is not found, 404 response is returned.

    **Authors**: Gagandeep Singh
    """
    def actual_decorator(func):
        def wrap(request, org, survey_uid=None, *args, **kwargs):
            # Get user
            reg_user = request.user.registereduser

            # Obtain survey_uid
            # (a) Check in url regex
            if survey_uid is None:
                # (b) Obtain from GET and (c) then from POST
                survey_uid = request.GET.get('survey_uid', request.POST.get('survey_uid', None) )

                if survey_uid is None:
                    raise Http404("Invalid link.")

            # Now check survey access permission
            try:
                if org is not None:
                    # Context: Organization
                    try:
                        filters = copy.deepcopy(request.permissions['surveys.survey']['data_access'])
                        filters['ownership'] = Survey.OWNER_ORGANIZATION
                        filters['organization_id'] = org.id
                        filters['survey_uid'] = survey_uid

                        survey = Survey.objects.get(**filters)
                    except TypeError:
                        # TypeError: If filters is None
                        if exception_type == 'api':
                            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to perform this action.").gen_http_response()
                        else:
                            return HttpResponseForbidden("You do not have permissions to access this page.")
                else:
                    # Context: Individual
                    filters = {
                        'ownership': Survey.OWNER_INDIVIDUAL,
                        'survey_uid': survey_uid,
                        'created_by_id': request.user.id
                    }
                    survey = Survey.objects.get(**filters)

                return func(request, org, survey, *args, **kwargs)

            except Survey.DoesNotExist:
                if exception_type == 'api':
                    return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to perform this action.").gen_http_response()
                else:
                    return HttpResponseForbidden("You do not have permissions to access this page.")

        return wrap
    return actual_decorator

