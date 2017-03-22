# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
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
# --- /BSP Feedback ---
# ==================== /Console ====================

