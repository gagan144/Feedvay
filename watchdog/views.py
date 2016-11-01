# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from utilities.decorators import registered_user_only
from utilities.api_utils import ApiResponse
from watchdog.models import *
from watchdog.forms import *


# ---------- Report Problem ----------
@registered_user_only
def report_problem_new(request):
    """
    View to handle new problem reported a user. User may or may not be logged in.
    :return: Http 200 JSON as per :class:`utilities.api_utils.ApiResponse`.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        form_report = ReportedProblemForm(request.POST)

        # Validate form
        if form_report.is_valid():
            form_data = form_report.cleaned_data
            for_current_page = True if form_data['current_page'] == 'yes' else False
            user = request.user if request.user.is_authenticated() else None

            new_problem = ReportedProblem.objects.create(
                platform = form_data['platform'],
                url = form_data['url'] if for_current_page else None,
                title = form_data['title'],
                description = form_data['description'],
                user = request.user,
                email_id = user.email if user else None
            )

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Incomplete submission.').gen_http_response()
    else:
        # Forbidden GET
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use POST.').gen_http_response()

# ---------- /Report Problem ----------

# ---------- Suggestions ----------
@registered_user_only
def suggestion_new(request):
    """
    View to handle new suggestion made by the user. User may or may not be logged in.
    :return: Http 200 JSON as per :class:`utilities.api_utils.ApiResponse`.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        form_sugg = SuggestionForm(request.POST)

        # Validate form
        if form_sugg.is_valid():
            form_data = form_sugg.cleaned_data
            for_current_page = True if form_data['current_page'] == 'yes' else False
            user = request.user if request.user.is_authenticated() else None

            new_sugg = Suggestion.objects.create(
                platform = form_data['platform'],
                url = form_data['url'] if for_current_page else None,
                title = form_data['title'],
                description = form_data['description'],
                user = request.user,
            )

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Incomplete submission.').gen_http_response()
    else:
        # Forbidden GET
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use POST.').gen_http_response()

# ---------- /Suggestions ----------
