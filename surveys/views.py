# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.http.response import Http404
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from django_fsm import TransitionNotAllowed

import json
from django.views.decorators.csrf import csrf_exempt

from surveys.models import Survey, SurveyPhase, SurveyCategory, SurveyResponse
from surveys.decorators import *
from languages.models import Language
from form_builder.utils import GeoLocation
from accounts.models import RegisteredUser
from utilities.decorators import registered_user_only
from utilities.api_utils import ApiResponse

# TODO: Mobile/Source validation firewall
def open_survey_form(request, survey_uid, phase_id=None):
    """
    View to open a survey form. If survey is simple, default phase is opened else phase_id is used.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    try:
        survey = Survey.objects.get(survey_uid=survey_uid)

        # Check status
        if survey.status == Survey.ST_READY:
            # Check date
            now = timezone.now().date()

            if survey.start_date <= now <= survey.end_date:
                #TODO: Audience filter

                # Obtain phase
                if survey.type == Survey.TYPE_SIMPLE:
                    phase = survey.phases[0]
                else:
                    try:
                        phase = survey.phases.filter(id=phase_id)
                    except SurveyPhase.DoesNotExist:
                        raise Survey.DoesNotExist("Invalid survey phase.")

                # --- All check passed ---
                form = phase.form
                template = 'themes/{}/form_base.html'.format(form.theme_skin.theme.code)

                data = {
                    'context': 'SURVEY',
                    'survey': survey,
                    'phase': phase,

                    'form': form,
                    'title': survey.title,
                    'theme': form.theme_skin.theme,
                    'skin': form.theme_skin,
                    'lookup_translations': form.get_translation_lookup(),
                    'DEFAULT_LANGUAGE_CODE': Language.DEFAULT_LANGUAGE_CODE,    # Fallback language incase translation not found

                    #TODO: Set user properties
                    'reg_user': RegisteredUser.objects.get(user__username=request.GET['username']),
                    'USER_DEFAULT_LANG_CODE': 'hin'
                }
                return render(request, template, data)
                # --- /All check passed ---
            else:
                raise Http404("Sorry! This survey has been completed.")

        elif survey.status == Survey.ST_STOPPED:
            raise Http404("Sorry! This survey has been concluded.")
        else:
            raise Http404("This survey is not currently active. Please try some other time.")

    except Survey.DoesNotExist:
        # Invalid link
        raise Http404("Invalid survey.")

# TODO: Mobile/Source validation firewall
@csrf_exempt
def submit_survey_response(request):
    """
    View to submit a response for survey phase.

    **Points**:

        - It does not block late submission.
        - All responses are recorded irrespective of survey status.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        token = request.POST['token']

        response_json = json.loads(request.POST['response'])

        response_uid = response_json['response_uid']
        form_version = response_json['form_version']

        try:
            survey = Survey.objects.get(survey_uid=response_json['survey_uid'])
            phase = survey.phases.get(id=response_json['phase_id'])
            form = phase.form

            version_obsolete = False if str(form.version) == form_version else True

            if not SurveyResponse.objects.filter(response_uid=response_uid).count():
                survey_response = SurveyResponse.objects.create(
                    survey_uid      = str(survey.survey_uid),
                    phase_id        = str(phase.id),
                    form_id         = str(form.id),
                    form_version    = form_version,
                    version_obsolete = version_obsolete,

                    app_version     = response_json['app_version'],
                    user            = SurveyResponse.UserInformation(**response_json['user']) if response_json['user'] else None,
                    end_point_info  = SurveyResponse.EndPointInformation(**response_json['end_point_info']),
                    language_code   = response_json["language_code"],

                    response_uid    = response_uid,
                    constants       = response_json['constants'],
                    answers         = response_json['answers'],
                    answers_other   = response_json['answers_other'],
                    calculated_fields = response_json['calculated_fields'],

                    timezone_offset        = response_json['timezone_offset'],
                    response_date   = timezone.datetime.strptime(response_json['response_date'],"%Y-%m-%dT%H:%M:%S"), # parse(response_json['response_date']),
                    start_time      = timezone.datetime.strptime(response_json['start_time'],"%Y-%m-%dT%H:%M:%S"), # parse(response_json['start_time']),
                    end_time        = timezone.datetime.strptime(response_json['end_time'],"%Y-%m-%dT%H:%M:%S"), # parse(response_json['end_time']),
                    duration        = response_json['duration'],

                    location        = SurveyResponse.LocationInformation(**response_json['location']) if response_json['location'] else None,

                    flags           = SurveyResponse.ResponseFlags(
                                           description_read = response_json['flags']['description_read'],
                                           instructions_read = response_json['flags']['instructions_read'],
                                           suspect = response_json['flags']['suspect'],
                                           suspect_reasons = response_json['flags']['suspect_reasons']
                                      )
                )

                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Survey response successfully submitted.').gen_http_response()

            else:
                return ApiResponse(status=ApiResponse.ST_IGNORED, message='Duplicate response received.').gen_http_response()

        except Survey.DoesNotExist:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Invalid survey.').gen_http_response()
        except SurveyPhase.DoesNotExist:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Invalid survey.').gen_http_response()

    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

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
        raise Http404("Invalid link.")

@registered_user_only
@survey_access_firewall
def console_survey_transit(request, survey):
    """
    API view to transit survey status.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        action = request.POST['action']
        try:

            # Check & make transition.
            if action == 'ready':
                survey.trans_ready()
            elif action == 'pause':
                survey.trans_pause()
            elif action == 'resume':
                survey.trans_resume()
            elif action == 'stop':
                survey.trans_stop()
            else:
                # Invalid transition
                return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Invalid action.').gen_http_response()

            survey.save()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok').gen_http_response()

        except TransitionNotAllowed:
            return ApiResponse(status=ApiResponse.ST_NOT_ALLOWED, message='You cannot perform this action.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

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
