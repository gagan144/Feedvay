# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import resolve_url,Http404
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import REDIRECT_FIELD_NAME
from django.conf import settings

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