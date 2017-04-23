# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import resolve_url,Http404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import REDIRECT_FIELD_NAME
from django.conf import settings
from django.contrib import auth
from functools import wraps
from django.db.models import Q

from accounts.utils import ClassifyRegisteredUser, has_necessary_permissions
# from clients.models import Organization, OrganizationMember
from utilities.api_utils import ApiResponse

def staff_user_only(function, login_url=settings.LOGIN_URL_STAFF, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Django view decorator to only allow logged in 'staff' or 'superuser' users only.
    If user is not logged in, it redirects to login page, otherwise returns 404.

    **Authors**: Gagandeep Singh
    """
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            if user.is_active and (user.is_staff or user.is_superuser):
                return function(request, *args, **kwargs)
            else:
                raise Http404("Permissions denied. Only staff users allowed.")
        else:
            path = request.get_full_path()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def registered_user_only(function, login_url=settings.LOGIN_URL, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Django view decorator to only allow logged in 'verified' registered user only.
    In case of check failure, it redirects to login page, otherwise returns 404.

    **Authors**: Gagandeep Singh
    """
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            user_class = ClassifyRegisteredUser.classify(user.username)

            if user_class == ClassifyRegisteredUser.VERIFIED:
                return function(request, *args, **kwargs)
            else:
                auth.logout(request)

        # In case of all check failure
        path = request.get_full_path()
        resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
        return redirect_to_login(path, resolved_login_url, redirect_field_name)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def organization_console(required_perms=None, all_required=True, exception_type='response', allow_bypass=False):
    """
    Django view decorator to allow only organization related console page with required permissions.
    This decorator depends upon :class:`console.middleware.OrgConsoleMiddleware` which is responsible
    authenticating user membership with the organization. After membership check, this decorator
    verifies that it registered user has required permissions or not.

    Also, the view on which this decorator is used must except an argument ``org``.

    :param required_perms: String or list of permission key of format ``<app-label>.<model-name>.<perm-codename>``.
    :param all_required: If True, all permissions are required else atleast one.
    :param exception_type: Type of forbidden response - ``response``: 403 page with message,
        ``api``: Forbidden response as per :class:`utilities.api_utils.ApiResponse`.
    :param allow_bypass: (Default False) If True, allows access to view even when it is accessed without
        context of an organization.


    **Points**:

        - This decorator must be user after ``registered_user_only``. It expects registered user.
        - Deleted organization and not included in the query.
        - If everything is ok:

            - It sets ``curr_org`` in ``request``.
            - It sets ``permissions`` in ``request``.
            - Passes the argument ``org`` to the view.


    **For views accessible in both with or without context of an organization**:
    If the view allows access in both cases, with out without organization, set option ``allow_bypass`` as True. In
    such a case if request parameter contains ``c`` then organization access will be checked along with permissions.
    However, if ``c`` is not present, it simply bypasses the check allowing access to the view. Thus it is the
    responsibility of the view to handle both cases along with permissions needed. View parameter ``org`` will
    be ``None`` if not in context of organization.


    **Failure behavior:**

        - If ``request`` does not have attribute ``curr_org``: returns Http404


    .. warning::
        If ``allow_bypass`` is set ``True``, it the responsibility of the view to handle both cases.

    **Authors**: Gagandeep Singh
    """

    def actual_decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                # (a) Organization permissions already checked in `console.middleware.OrgConsoleMiddleware`
                reg_user = request.user.registereduser
                org = request.curr_org

                # (b) Check permissions
                perm_json = reg_user.get_all_permissions(org)

                if required_perms is not None:
                    is_permitted = has_necessary_permissions(perm_json, required_perms, all_required)

                    if not is_permitted:
                        if exception_type == 'api':
                            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to access this page or perform action.").gen_http_response()
                        else:
                            return HttpResponseForbidden("You do not have permissions to access this page.")

                # (c) Set permissions in request
                request.permissions = perm_json

                return func(request, org=org, *args, **kwargs)

            except AttributeError:
                # AttributeError: 'curr_org' was not in request
                if allow_bypass:
                    # Allow to pass without organization
                    return func(request, org=None, *args, **kwargs)
                else:
                    # Raise 404 as it not not allowed with organization
                    raise Http404("Invalid link.")

        return wrapper
    return actual_decorator


