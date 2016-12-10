# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.http.response import Http404
from django.shortcuts import render

from surveys.models import Survey, SurveyPhase
from languages.models import Language
from form_builder.utils import GeoLocation
from utilities.decorators import registered_user_only

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

    reg_user = request.user.registereduser

    try:
        survey = Survey.objects.get(survey_uid=survey_uid, created_by_id=reg_user.id)

        data ={
            'survey': survey,
            'app_name': 'app_survey_panel'
        }
        return render(request, 'surveys/console/survey_panel.html', data)
    except Survey.DoesNotExist:
        raise Http404("invalid link.")

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
