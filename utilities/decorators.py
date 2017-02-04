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

from accounts.utils import ClassifyRegisteredUser
from clients.models import Organization, OrganizationMember

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

def organization_console(function):
    """
    Django view decorator to allow only organization related console page.
    This decorator also authenticates if user is a member in that organization thus
    this decorator must be user after ``registered_user_only``.

    This decorator expects the view to receive GET parameter ``c`` as organization
    unique id using which it finds user organization.

    Also, the view on which this decorator is used must except an argument ``org``.

    If everything is ok:

        - It sets ``curr_org`` in ``request``
        - Passes the argument ``org`` to the view.

    **Failure behavior:**

        - If ``c`` is not present in GET params: returns Http404
        - If Organization not found: HttpResponseForbidden
        - If user is not a member of the organization: HttpResponseForbidden

    .. note::
        This decorators does not check user authentication. This decorator must be used after
        any authentication check decorator.

    **Authors**: Gagandeep Singh
    """
    def wrap(request, *args, **kwargs):

        try:
            org_uid = request.GET['c']
            reg_user = request.user.registereduser

            # Get organization to which this user is a member
            org = Organization.objects.get(
                organizationmember__organization__org_uid = org_uid,
                organizationmember__registered_user = reg_user
            )

            request.curr_org = org
            return function(request, org=org, *args, **kwargs)

        except (KeyError, ValueError) as ex:
            # KeyError: 'c' was not in GET params, ValueError: If c is badly formed hexadecimal UUID string, DoesNotExist: Org not found
            raise Http404("Invalid link.")
        except Organization.DoesNotExist:
            # Organization not found or user is not a member of the organization
            return HttpResponseForbidden('You do not have permissions to access this page.')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

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
