# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from clients.models import Organization
from utilities.decorators import registered_user_only, organization_console

@registered_user_only
@organization_console
def console_org_settings(request, org):
    """
    View for organization settings. Only applicable for brand console.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "app_name": "app_org_settings",
        "Organization": Organization
    }
    return render(request, 'clients/console/org_settings.html', data)
