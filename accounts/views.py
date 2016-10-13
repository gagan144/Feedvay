# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from accounts.forms import *

# ---------- Registration ----------
def registration(request):
    """
    View to handle registration. If called with GET opens registrations form otherwise on POST
    register a user with given details.

    **Authors**: Gagandeep Singh
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home_user'))
    if not settings.REGISTRATION_OPEN:
        return HttpResponseRedirect(reverse('accounts_registration_closed'))

    country_tel_code = '+91'
    data = {
        'country_tel_code': country_tel_code
    }
    form_reg = RegistrationForm()

    if request.method.lower() == 'post':
        data_reg = request.POST.copy()
        data_reg['country_tel_code'] = country_tel_code
        form_reg = RegistrationForm(data_reg)
        pass

    data['form_reg'] = form_reg
    return render(request, 'accounts/registration.html', data)

def registration_closed(request):
    data = {}
    return render(request, 'accounts/registration_closed.html', data)
# ---------- /Registration ----------
