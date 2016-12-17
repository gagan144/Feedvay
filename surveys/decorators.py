# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.http import HttpResponseForbidden
from django.shortcuts import Http404

from surveys.models import Survey

def survey_access_firewall(function):
    """
    Django view decorator for survey that act as firewall before accessing a survey. It assumes that
    user session has been authenticated and does the following:

        - Obtain survey_uid. If not passed, return 404 response.
        - Verify the survey based on user access permissions and allow/block accordingly.
        - If allowed, obtain survey object and pass to the actual view in parameter ``survey``.
        - If not allowed, return 403 forbidden response.


    All views using this decorator are expected to receive ``survey_uid`` in one of the following ways:

        - In url regex. Example: ``/path/to/survey/<survey_uid>/``
        - In GET parameters: ``/path/to/survey/?survey_uid=<survey_uid>``
        - In POST parameters: ``survey_uid=<survey_uid>``

        The order of evaluation is the same as listed and if survey_uid is not found, 404 response is returned.

    **Authors**: Gagandeep Singh
    """
    def wrap(request, survey_uid=None, *args, **kwargs):
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
            # TODO: Currently only checking for individual
            survey = Survey.objects.get(survey_uid=survey_uid, created_by_id=reg_user.id)

            return function(request, survey, *args, **kwargs)
        except Survey.DoesNotExist:
            # Does not have curr_brand in request; Invalid access
            return HttpResponseForbidden("Invalid link or access not allowed.")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap