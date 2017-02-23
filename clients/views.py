# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseForbidden

from clients.models import Organization, OrganizationMember
from clients import operations
from clients import forms as forms_clients
from accounts.models import OrganizationRole
from accounts.decorators import registered_user_only, organization_console
from accounts.utils import get_all_superuser_permissions
from accounts import forms as forms_account
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


@registered_user_only
@organization_console()
def console_team(request, org):
    """
    Django view to manage organization teams in terms of roles, members etc.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        'app_name': 'app_team'
    }

    return render(request, 'clients/console/team/team.html', data)

# ----- User, permissions , roles & data access -----
# --- Roles ---
@registered_user_only
@organization_console(required_perms='accounts.organizationrole.add_organizationrole')
def console_organization_role_new(request, org):
    """
    Django view to all new organization roles.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        'app_name': 'app_org_role_add',
        'list_all_permissions': get_all_superuser_permissions()
    }

    return render(request, 'clients/console/team/organization_role_add.html', data)

@registered_user_only
@organization_console(required_perms='accounts.organizationrole.add_organizationrole')
def console_organization_role_create(request, org):
    """
    An API view to create new role in the organization.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        # Set data
        data = {
            "name": request.POST['name'],
            "permissions": request.POST.getlist('permissions[]'),
            "organization": org.id
        }

        form_new_role = forms_account.OrganizationRoleForm(data)

        if form_new_role.is_valid():
            form_new_role.save(created_by=request.user)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_new_role.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console(required_perms='accounts.organizationrole.change_organizationrole')
def console_organization_role_edit(request, org, org_role_id):
    """
    Django view to all edit an organization role.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    try:
        filters = request.permissions['accounts.organizationrole']['data_access']
        filters['organization_id'] = org.id
        filters['id'] = org_role_id

        # org_role = OrganizationRole.objects.get(organization_id=org.id, pk=org_role_id)
        org_role = OrganizationRole.objects.get(**filters)
    except (TypeError, OrganizationRole.DoesNotExist):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")

    data = {
        'app_name': 'app_org_role_edit',
        'org_role': org_role,
        'list_all_permissions': get_all_superuser_permissions()
    }

    return render(request, 'clients/console/team/organization_role_edit.html', data)

@registered_user_only
@organization_console(required_perms='accounts.organizationrole.change_organizationrole')
def console_organization_role_edit_save(request, org, org_role_id):
    """
    An API view to save role changes in the organization.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = request.permissions['accounts.organizationrole']['data_access']
            filters['organization_id'] = org.id
            filters['id'] = org_role_id

            # org_role = OrganizationRole.objects.get(organization_id=org.id, pk=org_role_id)
            org_role = OrganizationRole.objects.get(**filters)
        except (TypeError, OrganizationRole.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to change this role.")

        # Set data
        data = {
            "name": request.POST['name'],
            "permissions": request.POST.getlist('permissions[]'),
            "organization": org.id
        }

        form_new_role = forms_account.OrganizationRoleForm(data, instance=org_role)

        if form_new_role.is_valid():
            form_new_role.save()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_new_role.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()
# --- Roles ---

# --- Members, invitation ---
@registered_user_only
@organization_console(required_perms='clients.organizationmember.add_organizationmember')
def console_member_new(request, org):
    """
    View to open form to add/invite a new member in the organization.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    country_tel_code = '+91'    #TODO: Set default country_tel_code
    data = {
        "app_name": "app_mem_invite",
        'country_tel_code': country_tel_code,
        'list_roles': OrganizationRole.objects.filter(organization_id=org.id),
        'list_all_permissions': get_all_superuser_permissions()
    }

    return render(request, 'clients/console/team/member_add.html', data)

@registered_user_only
@organization_console(required_perms='clients.organizationmember.add_organizationmember')
def console_member_invite(request, org):
    """
    API view to add/invite a new member in the organization. User submit his form to this
    view.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        country_tel_code = '+91'    #TODO: Set default country_tel_code

        # Set data
        data = request.POST.copy()
        data['organization'] = org.id
        data['country_tel_code'] = country_tel_code
        if request.POST.get('roles[]', None):
            data['roles'] = request.POST.getlist('roles[]')
            del data['roles[]']
        if request.POST.get('permissions[]', None):
            data['permissions'] = request.POST.getlist('permissions[]')
            del data['permissions[]']

        del data['c']
        data = data.dict()


        form_new_mem = forms_clients.AddInviteMemberForm(data)

        if form_new_mem.is_valid():
            form_new_mem.save(created_by=request.user)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_new_mem.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console(required_perms='clients.organizationmember.change_organizationmember')
def console_member_edit(request, org, org_mem_id):
    """
    Django view to all edit an organization membership details.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    try:
        filters = request.permissions['clients.organizationmember']['data_access']

        filters['organization_id'] = org.id
        filters['id'] = org_mem_id
        filters['deleted'] = False

        org_mem = OrganizationMember.objects.get(**filters)
        member = org_mem.registered_user
    except (TypeError, OrganizationRole.DoesNotExist):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")

    country_tel_code = '+91'    #TODO: Set default country_tel_code
    data = {
        'app_name': 'app_org_mem_edit',
        'org_mem': org_mem,

        'is_superuser': member.superuser_in.filter(id=org.id).exists(),
        'roles': member.roles.filter(organization_id=org.id),
        'permissions': member.permissions.filter(userpermission__organization_id=org.id, userpermission__registered_user_id=member.id),

        'country_tel_code': country_tel_code,
        'list_roles': OrganizationRole.objects.filter(organization_id=org.id),
        'list_all_permissions': get_all_superuser_permissions()
    }

    return render(request, 'clients/console/team/member_edit.html', data)

@registered_user_only
@organization_console(required_perms='clients.organizationmember.add_organizationmember')
def console_member_edit_save(request, org, org_mem_id):
    """
    API view to save changes for a member in the organization. User submit his form to this
    view.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':

        # Set data
        data = request.POST.copy()
        data['org_mem'] = org_mem_id
        if request.POST.get('roles[]', None):
            data['roles'] = request.POST.getlist('roles[]')
            del data['roles[]']
        if request.POST.get('permissions[]', None):
            data['permissions'] = request.POST.getlist('permissions[]')
            del data['permissions[]']

        del data['c']
        data = data.dict()

        form_edit_mem = forms_clients.EditMemberForm(data)

        if form_edit_mem.is_valid():
            form_edit_mem.save(created_by=request.user)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_edit_mem.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console(required_perms='clients.organizationmember.delete_organizationmember')
def console_member_remove(request, org, org_mem_id):
    """
    API view to remove a member of the organization.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = request.permissions['clients.organizationmember']['data_access']

            filters['organization_id'] = org.id
            filters['id'] = org_mem_id
            filters['deleted'] = False

            org_mem = OrganizationMember.objects.get(**filters)
        except (TypeError, OrganizationRole.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to remove this member.")


        confirm = int(request.POST.get('confirm', 0))

        if not confirm:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please confirm your action.').gen_http_response()
        else:
            org_mem.mark_deleted(confirm=True)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()
# --- /Members, invitation ---
# ----- /User, permissions , roles & data access -----

# ==================== /Console ====================
