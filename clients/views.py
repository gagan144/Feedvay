# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from clients.models import Organization
from clients import operations
from accounts.decorators import registered_user_only, organization_console
from utilities.api_utils import ApiResponse

# ==================== Console ====================
@registered_user_only
@organization_console()
def console_org_home(request, org):
    """
    View for organization home.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        "app_name": "app_home_org"
    }
    return render(request, 'clients/console/home_org.html', data)

@registered_user_only
@organization_console(required_perms='clients.organization.change_organization')
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

@registered_user_only
@organization_console(required_perms='clients.organization.change_organization', exception_type='api')
def console_org_submit_changes(request, org):
    """
    An API view to submit changes in organization. This view receives only changed fields and are
    updated immediately.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        # (b) Update information
        data = request.POST.copy()
        del data['c']
        try:
            operations.update_organization(request.user, org, data, request.FILES)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='All updates made successfully').gen_http_response()
        except Exception as ex:
            return ApiResponse(status=ApiResponse.ST_FAILED, message=ex.message).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# ----- User permissions , roles & data access -----
@registered_user_only
@organization_console(required_perms='accounts.organizationrole')
def console_organization_roles(request, org):
    """
    Django view to display all organization roles.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        'app_name': 'app_org_roles'
    }

    return render(request, 'clients/console/iam/organization_roles.html', data)

@registered_user_only
@organization_console(required_perms='accounts.organizationrole')
def console_organization_role_add(request, org):
    """
    Django view to all new organization roles.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        'app_name': 'app_org_role_add'
    }

    return render(request, 'clients/console/iam/organization_role_add.html', data)

# ----- /User permissions , roles & data access -----

# ==================== /Console ====================
