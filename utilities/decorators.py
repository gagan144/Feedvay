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
import re
from django.db.models import Q
from django.core.cache import cache

from accounts.utils import ClassifyRegisteredUser, lookup_permission
from clients.models import Organization, OrganizationMember
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


def organization_console(required_perms=None, all_required=True, exception_type='response'):
    """
    Django view decorator to allow only organization related console page.
    This decorator authenticates if user is a member in that organization and has required permissions.

    This decorator expects the view to receive GET/POST parameter ``c`` as organization
    unique id using which it finds user organization.

    Also, the view on which this decorator is used must except an argument ``org``.

    :param required_perms: String or list of permission key of format ``<app-label>.<model-name>.<perm-codename>``.
    :param all_required: If True, all permissions are required else atleast one.
    :param exception_type: Type of forbidden response - ``response``: 403 page with message,
        ``api``: Forbidden response as per :class:`utilities.api_utils.ApiResponse`.


    **Points**:

        - This decorator must be user after ``registered_user_only``. It expects registered user.
        - Deleted organization and not included in the query.
        - If everything is ok:

            - It sets ``curr_org`` in ``request``.
            - It sets ``permissions`` in ``request``.
            - Passes the argument ``org`` to the view.

    **Failure behavior:**

        - If ``c`` is not present in GET/POST params: returns Http404
        - If Organization not found: HttpResponseForbidden
        - If user is not a member of the organization: HttpResponseForbidden

    **Authors**: Gagandeep Singh
    """

    def actual_decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                # Fetch 'c' para, from GET or POST
                if request.GET.get('c', None):
                    org_uid = request.GET['c']
                else:
                    org_uid = request.POST['c']

                reg_user = request.user.registereduser

                # (a) Get organization to which this user is a member
                org = Organization.objects.get(
                    Q(organizationmember__organization__org_uid = org_uid, organizationmember__registered_user = reg_user) &
                    ~Q(status=Organization.ST_DELETED)
                )
                request.curr_org = org

                # (b) Check permissions
                perm_json = reg_user.get_all_permissions(org)

                if required_perms is not None:
                    # Make list if not required_perms is string
                    if isinstance(required_perms, str) or isinstance(required_perms, unicode):
                        list_perms = [required_perms]
                    else:
                        list_perms = required_perms

                    # Loop and check presence
                    is_permitted = True
                    for perm_key in list_perms:
                        is_present = lookup_permission(perm_json, perm_key)

                        if all_required:
                            # All required: AND operation
                            is_permitted = is_permitted and is_present
                            if not is_permitted:
                                break
                        else:
                            # Atleast one required: OR operation
                            is_permitted = is_permitted or is_present

                    if not is_permitted:
                        msg = "You do not have permissions to access this page."
                        if exception_type == 'api':
                            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message=msg).gen_http_response()
                        else:
                            return HttpResponseForbidden(msg)

                # (c) Set permissions in request
                request.permissions = perm_json

                return func(request, org=org, *args, **kwargs)

            except (KeyError, ValueError) as ex:
                # KeyError: 'c' was not in GET params, ValueError: If c is badly formed hexadecimal UUID string, DoesNotExist: Org not found
                raise Http404("Invalid link.")
            except Organization.DoesNotExist:
                # Organization not found or user is not a member of the organization
                return HttpResponseForbidden('You do not have permissions to access this page.')
        return wrapper
    return actual_decorator


def brand_console(function):
    """
    Django view decorator to allow only brand related console page.
    In case of failure, returns http 404.

    .. note::
        This decorators does not check user authentication. This decorator must be used after
        any authentication check decorator.

    **Authors**: Gagandeep Singh
    """
    def wrap(request, *args, **kwargs):
        try:
            curr_brand = request.curr_brand
            return function(request, *args, **kwargs)
        except AttributeError:
            # Does not have curr_brand in request; Invalid access
            raise Http404("Invalid link.")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def minified_response(f):
    """
    Django view decorator to minify html page.

    **Authors**: Gagandeep Singh
    """
    @wraps(f)
    def minify(*args, **kwargs):
        response = f(*args, **kwargs)

        content = response.content

        re_whitespace = re.compile('(^\s*|^\s+|\n|\s+$)', re.MULTILINE)

        content = re_whitespace.sub('', content)

        response.content = content
        return response

    return minify
