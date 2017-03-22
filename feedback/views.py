# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from languages.models import Language
from form_builder.utils import GeoLocation
from accounts.decorators import registered_user_only, organization_console

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
def console_bsp_new_feedback(request, org):
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
# --- /BSP Feedback ---
# ==================== /Console ====================

