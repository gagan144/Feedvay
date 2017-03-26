# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.conf import settings
import json
import copy

from accounts.decorators import registered_user_only, organization_console
from languages.models import Language
from form_builder.models import ThemeSkin
from form_builder.utils import GeoLocation
from form_builder import operations as ops
from feedback.models import BspFeedbackForm
from utilities.api_utils import ApiResponse

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
        'GeoLocation': GeoLocation
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
        'GeoLocation': GeoLocation
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
            return HttpResponseForbidden("You do not have permissions to access this page.")

        form_data = json.loads(request.POST['form_data'])
        translation = json.loads(request.POST['translations'])

        form_saved = ops.create_update_form(bsp_fdbk_form, form_data, translation)

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok', is_ready=form_saved.is_ready, form_id=form_saved.id).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()
# --- /BSP Feedback ---
# ==================== /Console ====================

