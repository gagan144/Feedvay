# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings
import json
import copy
from django.views.decorators.csrf import csrf_exempt

from mongoengine.queryset import DoesNotExist as DoesNotExist_mongo

from accounts.decorators import registered_user_only, organization_console
from languages.models import Language
from form_builder.models import ThemeSkin
from form_builder.utils import GeoLocation
from form_builder import operations as ops
from form_builder.fields import AiTextDirectives
from feedback.models import BspFeedbackForm
from feedback.fixed_questions import *
from market.models import BusinessServicePoint, BspTypes, Brand
from accounts.models import RegisteredUser
from storeroom.models import ResponseQueue
from utilities.api_utils import ApiResponse

#TODO: Mobile/Web access checks
def open_bsp_feedback(request, bsp_id):
    """
    View to open BSP feedback form. Incase where there is no feedback form associated
    with BSP, Rating-Review page is displayed.


    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    # Gather data
    try:
        username = request.GET['username']

        bsp = BusinessServicePoint.objects.get(pk=bsp_id)
    except KeyError, DoesNotExist_mongo:
        # Key Error: username not present,  DoesNotExist_mongo: Invalid BSP
        return HttpResponseForbidden("Invalid page request.")

    # Get feedback form.
    try:
        form = bsp.feedback_form.form
    except AttributeError:
        # AttributeError: bsp.feedback_form is None
        form = None

    # Check form exists and is ready
    if form and form.is_ready:
        # Feedback form found, prepare form render data
        template = 'themes/{}/form_base.html'.format(form.theme_skin.theme.code)

        lookup_translations = form.get_translation_lookup()
        for ques in BspFixedQuestions.questions:
            trans = ques.translation
            # print trans.pk
            lookup_translations[str(trans.pk)] = trans

        data = {
            'context': 'BSP_FEEDBACK',
            'bsp': bsp,

            'form': form,
            'title': bsp.name,
            'lookup_translations': lookup_translations,
            'FIXED_QUESTIONS': BspFixedQuestions.questions,
            'DEFAULT_LANGUAGE_CODE': Language.DEFAULT_LANGUAGE_CODE,    # Fallback language incase translation not found

            # TODO: Set user properties
            'reg_user': RegisteredUser.objects.get(user__username=username),
            'USER_DEFAULT_LANG_CODE': 'eng'
        }
        return render(request, template, data)
    else:
        # Form is None; render default rating-review form.
        raise NotImplementedError("No Feedback Form associated: Render rating-review form.")  #TODO: Render rating-review form



# TODO: Mobile/Web access checks
@csrf_exempt
def submit_bsp_feedback_response(request):
    """
    API view to submit BSP feedback response. This view receives response
    submitted by the user and is queued for processing.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        token = request.POST['token']

        response_data = request.POST['response']

        resp_queue = ResponseQueue.objects.create(
            context = ResponseQueue.CT_BSP_FEEDBACK,
            data    = response_data,
        )

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Response queued for processing.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


# ==================== Console ====================
# --- BSP Feedback ---
@registered_user_only
@organization_console()
def console_bsp_feedback_panel(request, org):
    """
    Django view to manage organization BSP Feedback.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        'app_name': 'app_bspfeedback_panel',
    }

    return render(request, 'feedback/console/bsp_feedback_panel.html', data)

@registered_user_only
@organization_console('feedback.bspfeedbackform.add_bspfeedbackform')
def console_bsp_feedback_new(request, org):
    """
    Django view to open form builder to create new BSP feedback form.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        'app_name': 'app_form_builder',
        'TYPE': 'BSP_FEEDBACK',
        'list_languages': Language.objects.filter(active=True),
        'GeoLocation': GeoLocation,
        'BspFixedQuestions': BspFixedQuestions
    }

    return render(request, 'form_builder/form_designer.html', data)

@registered_user_only
@organization_console('feedback.bspfeedbackform.add_bspfeedbackform')
def console_bsp_feedback_create(request, org):
    """
    API view to create new BSP feedback form. User submit form data and
    new questionnaire is created.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        form_data = json.loads(request.POST['form_data'])
        translation = json.loads(request.POST['translations'])
        bsp_fdbk_form = BspFeedbackForm.objects.create(
            organization = org,
            title = form_data['title'],
            theme_skin = ThemeSkin.objects.get(theme__code=settings.DEFAULT_FORM_THEME['theme_code'], code=settings.DEFAULT_FORM_THEME['skin_code']),
            created_by = request.user
        )

        form_saved = ops.create_update_form(bsp_fdbk_form, form_data, translation)

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok', is_ready=form_saved.is_ready, form_id=form_saved.id).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console('feedback.bspfeedbackform.change_bspfeedbackform')
def console_bsp_feedback_manage(request, org, form_id):
    """
    Django view to manage BSP Feedback form. This page allows user to associate BSP to the form.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    try:
        filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
        filters['organization_id'] = org.id
        filters['id'] = form_id

        bsp_fdbk_form = BspFeedbackForm.objects.get(**filters)
    except (TypeError, BspFeedbackForm.DoesNotExist):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")

    data = {
        'app_name': 'app_bspfeedback_manage',
        'form': bsp_fdbk_form,

        'list_brands': Brand.objects.filter(organization_id=org.id),
        "BusinessServicePoint": BusinessServicePoint,
        "BspTypes": BspTypes,
        "AWS_S3_CUSTOM_DOMAIN": settings.AWS_S3_CUSTOM_DOMAIN
    }

    return render(request, 'feedback/console/bsp_feedback_manage.html', data)


@registered_user_only
@organization_console('feedback.bspfeedbackform.change_bspfeedbackform')
def console_bsp_feedback_edit(request, org, form_id):
    """
    Django view to edit BSP Feedback form.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    try:
        filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
        filters['organization_id'] = org.id
        filters['id'] = form_id

        bsp_fdbk_form = BspFeedbackForm.objects.get(**filters)
    except (TypeError, BspFeedbackForm.DoesNotExist):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")

    data = {
        'app_name': 'app_form_builder',
        'TYPE': 'BSP_FEEDBACK',
        'form': bsp_fdbk_form,
        'list_languages': Language.objects.filter(active=True),
        'GeoLocation': GeoLocation,
        'BspFixedQuestions': BspFixedQuestions
    }

    return render(request, 'form_builder/form_designer.html', data)


@registered_user_only
@organization_console('feedback.bspfeedbackform.change_bspfeedbackform')
def console_bsp_feedback_edit_save(request, org, form_id):
    """
    API view to save BSP feedback form changes. User submit form data and form is updated.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
            filters['organization_id'] = org.id
            filters['id'] = form_id

            bsp_fdbk_form = BspFeedbackForm.objects.get(**filters)
        except (TypeError, BspFeedbackForm.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to access this page.").gen_http_response()

        form_data = json.loads(request.POST['form_data'])
        translation = json.loads(request.POST['translations'])

        form_saved = ops.create_update_form(bsp_fdbk_form, form_data, translation)

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok', is_ready=form_saved.is_ready, form_id=form_saved.id).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console(['feedback.bspfeedbackform.change_bspfeedbackform', 'feedback.bspfeedbackform.add_bspfeedbackform', 'feedback.bspfeedbackform.change_bspfeedbackform'], all_required=False)
def console_bsp_feedback_associate_bsp(request, org, form_id):
    """
    API view to associate BSP to Bsp Feedback Form. User submits selected bsp ids from
    UI and post request.

    .. note::
        It is necessary that all requested bsp gets attached. Some might be ignored
        due to the fact that they have already been associated to the form or user
        did not have access to some bsps as per his data access filter.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        # Check access to form
        try:
            filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
            filters['organization_id'] = org.id
            filters['id'] = form_id

            bsp_fdbk_form = BspFeedbackForm.objects.get(**filters)
        except (TypeError, BspFeedbackForm.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to access this page.").gen_http_response()

        # Get all BSP as per access filters
        try:
            filters_bsp = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
            filters_bsp['organization_id'] = org.id

            list_bsp_ids = request.POST.getlist('list_bsp_ids[]')
            if not len(list_bsp_ids):
                raise KeyError("'list_bsp_ids' is empty.")

            # Check if data access has pk__in
            if filters_bsp.has_key('pk__in'):
                # Take intersection
                list_bsp_ids = set(filters_bsp['pk__in']).intersection(list_bsp_ids)
                list_bsp_ids = list(list_bsp_ids)

            filters_bsp['pk__in'] = list_bsp_ids
        except KeyError:
            # list_bsp_ids not present in post params or was empty
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Missing parameters.').gen_http_response()

        filters_bsp['feedback_form__form_id__ne'] = bsp_fdbk_form.id

        # Attach bsp to the form
        list_bsps = BusinessServicePoint.objects.filter(**filters_bsp)
        count = 0
        for bsp in list_bsps:
            bsp.associate_feedback_form(bsp_fdbk_form, None, request.user)
            count += 1

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok', count=count).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console(['feedback.bspfeedbackform.change_bspfeedbackform', 'feedback.bspfeedbackform.add_bspfeedbackform', 'feedback.bspfeedbackform.change_bspfeedbackform'], all_required=False)
def console_bsp_feedback_deassociate_bsp(request, org, form_id):
    """
    API view to de-associate BSP from Bsp Feedback Form. User submits selected bsp ids from
    UI and post request.

    .. note::
        It is necessary that all requested bsp gets detached. Some might be ignored
        due to the fact that they have already been de-associated or user
        did not have access to some bsps as per his data access filter.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        # Check access to form
        try:
            filters = copy.deepcopy(request.permissions['feedback.bspfeedbackform']['data_access'])
            filters['organization_id'] = org.id
            filters['id'] = form_id

            bsp_fdbk_form = BspFeedbackForm.objects.get(**filters)
        except (TypeError, BspFeedbackForm.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to access this page.").gen_http_response()

        # Get all BSP as per access filters
        try:
            filters_bsp = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
            filters_bsp['organization_id'] = org.id

            list_bsp_ids = request.POST.getlist('list_bsp_ids[]')
            if not len(list_bsp_ids):
                raise KeyError("'list_bsp_ids' is empty.")

            # Check if data access has pk__in
            if filters_bsp.has_key('pk__in'):
                # Take intersection
                list_bsp_ids = set(filters_bsp['pk__in']).intersection(list_bsp_ids)
                list_bsp_ids = list(list_bsp_ids)

            filters_bsp['pk__in'] = list_bsp_ids
        except KeyError:
            # list_bsp_ids not present in post params or was empty
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Missing parameters.').gen_http_response()

        filters_bsp['feedback_form__form_id'] = bsp_fdbk_form.id

        # Attach bsp to the form
        list_bsps = BusinessServicePoint.objects.filter(**filters_bsp)
        count = 0
        for bsp in list_bsps:
            bsp.deassociate_feedback_form(confirm=True)
            count += 1

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok', count=count).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console('market.businessservicepoint.change_businessservicepoint')
def console_bsp_feedback_associate_form(request, org, bsp_id):
    """
    API view to associate BSP feedback form to a BSP.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        # Check access to bsp
        try:
            filters = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
            filters['organization_id'] = org.id
            filters['pk'] = bsp_id

            bsp = BusinessServicePoint.objects.get(**filters)
        except (TypeError, DoesNotExist_mongo):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to access this page.").gen_http_response()

        try:
            data = json.loads(request.POST['data'])

            form = BspFeedbackForm.objects.get(id=data['form_id'])
            ai_directives_json = data.get('ai_directives', {})
            ai_directives = AiTextDirectives(ai_directives_json)

            bsp.associate_feedback_form(form, ai_directives, request.user)

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok').gen_http_response()

        except KeyError:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Missing parameters.').gen_http_response()
        except BspFeedbackForm.DoesNotExist:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Invalid BSP.').gen_http_response()

    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# --- /BSP Feedback ---
# ==================== /Console ====================


