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
