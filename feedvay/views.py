# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import os

from utilities.decorators import staff_user_only


def home(request):
    """
    View for main site page.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "welcome": request.GET.get('welcome',False)
    }
    return render(request, 'home.html', data)


# ---------- Project Documentation serve ----------
def get_absolute_filename(filename='', safe=True):
    if not filename:
        return os.path.join(settings.DOCS_PATH, 'index.html')
    if safe and '..' in filename.split(os.path.sep):
        return get_absolute_filename(filename='')
    return os.path.join(settings.DOCS_PATH, filename)

@staff_user_only
def docs(request, filename=None):
    """
    A view that serves project documentation created using sphinx documentation module to
    logged in staff users only. The documentation created is in form of static html, js, css files
    and cannot be served insecurely through static configuration.

    This view technically does not provide actual file content but rather provides information
    about the file to the web server (nginx) which in turn serves the file.
    The view accepts a file url and simply sends back a response with absolute file path
    in 'X-Sendfile' header. The web server uses this information to serve the actual file.

    When the web server encounters X-Sendfile header, it fetches file from that path,
    handles caching, content-type, content-length, stream etc and servers the file.
    Please make sure that you have configured nginx accordingly.

    This is done to prevent django to load file into memory and perform unnecessary processing
    that consumes CPU & memory and blocks web server threads.

    Reference: http://zacharyvoase.com/2009/09/08/sendfile/

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    abs_filename = get_absolute_filename(filename)
    response = HttpResponse()
    del response['content-type'] # We'll let the web server guess this.
    response['X-Sendfile'] = abs_filename
    return response

# ---------- /Project Documentation serve ----------