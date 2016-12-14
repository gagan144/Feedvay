# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.http.response import Http404
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from surveys.models import Survey, SurveyPhase, SurveyCategory
from languages.models import Language
from form_builder.utils import GeoLocation
from utilities.decorators import registered_user_only
from utilities.api_utils import ApiResponse

# ==================== Console ====================
@registered_user_only
def console_surveys(request):
    """
    View to list all surveys for a registered user.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    reg_user = request.user.registereduser
    data ={
        'list_surveys': Survey.objects.filter(created_by_id=reg_user.id).only('id', 'category', 'survey_uid', 'title', 'description', 'start_date', 'end_date', 'surveyor_type', 'audience_type', 'status')
    }

    return render(request, 'surveys/console/surveys.html', data)

@registered_user_only
def console_survey_panel(request, survey_uid):
    """
    View to open control panel for a survey.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    # Currently for individual only.
    reg_user = request.user.registereduser

    try:
        survey = Survey.objects.get(survey_uid=survey_uid, created_by_id=reg_user.id)

        data ={
            'SURVEY': Survey,
            'survey': survey,
            'now': timezone.now(),
            'app_name': 'app_survey_panel',
            'list_categories': SurveyCategory.objects.filter(Q(active=True)|Q(id=survey.category_id)).only('id', 'name')
        }
        return render(request, 'surveys/console/survey_panel.html', data)
    except Survey.DoesNotExist:
        raise Http404("invalid link.")

@registered_user_only
def console_survey_save(request, survey_uid=None):
    """
    API view to save survey information. If survey_uid is ``None``, it means create new survey.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    # Current only for individual
    reg_user = request.user.registereduser

    if request.method.lower() == 'post':
        try:
            survey = Survey.objects.get(survey_uid=survey_uid, created_by_id=reg_user.id)

            from surveys.forms import SurveyEditForm
            form_survey = SurveyEditForm(request.POST, instance=survey)

            if form_survey.is_valid():
                if len(form_survey.changed_data):
                    form_survey.save()
                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok').gen_http_response()
            else:
                errors = dict(form_survey.errors)
                return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
        except Survey.DoesNotExist:
            return ApiResponse(status=ApiResponse.ST_UNAUTHORIZED, message='Invalid survey.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
def console_survey_phase_form_editor(request, survey_uid, phase_id=None):
    """
    View to open form editor for a survey phase.

    **Points**:

        - This view caters bothe simple & complex surveys.
        - If ``phase_id`` is not provided, it means survey must be ``simple`` and first phase is automatically picked.
        - If ``phase_id`` is provides, irrespective of the type, it opens editor for that phase.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    reg_user = request.user.registereduser
    try:
        if phase_id is None:
            # Simple survey
            survey = Survey.objects.get(type=Survey.TYPE_SIMPLE, survey_uid=survey_uid, created_by_id=reg_user.id)
            phase = survey.surveyphase_set.all()[0]
        else:
            # Complex survey
            survey = Survey.objects.get(survey_uid=survey_uid, created_by_id=reg_user.id)
            phase = survey.surveyphase_set.get(id=int(phase_id))

        data ={
            'survey': survey,
            'phase': phase,
            'form': phase.form,

            'app_name': 'app_form_builder',
            'list_languages': Language.objects.filter(active=True),
            'GeoLocation': GeoLocation
        }

        return render(request, 'form_builder/form_designer.html', data)
    except Survey.DoesNotExist:
        raise Http404("Invalid survey.")
    except SurveyPhase.DoesNotExist:
        raise Http404("Invalid survey phase.")
# ==================== /Console ====================
