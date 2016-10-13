# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings
import jwt

from django.contrib.auth.models import User
from accounts.forms import *
from accounts.models import *

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

    country_tel_code = '+91'    #TODO: Set default country_tel_code
    data = {
        'country_tel_code': country_tel_code
    }
    form_reg = RegistrationForm()

    if request.method.lower() == 'post':
        # Gather form data from POST
        data_reg = request.POST.copy()
        data_reg['country_tel_code'] = country_tel_code
        form_reg = RegistrationForm(data_reg)

        # TODO: Check username/ if already registered, redirect to verification

        # Validate form
        if form_reg.is_valid():
            form_data = form_reg.cleaned_data

            # Create all database entries in one atomic process
            with transaction.atomic():
                # Create 'User' model
                new_user = User(
                    username = form_data['mobile_no'],
                    first_name = form_data['first_name'],
                    last_name =  form_data['last_name'],
                    is_active = False
                )
                set_user_password(new_user, form_data['password'], False) # This will save user

                # Create 'RegisterUser'
                new_registered_user = RegisteredUser.objects.create(
                    user = new_user,
                    reg_method = RegisteredUser.REG_WEB_PORTAL,
                )

                # Transit status from 'lead' to 'verification_pending'
                new_registered_user.trans_registered()

            # TODO: Send all owls

            # Generate token & redirect to verification
            token = jwt.encode(
                {
                    'reg_user_id': new_registered_user.pk
                },
                settings.JWT_SECRET_KEY,
                algorithm = settings.JWT_ALOG
            )
            return HttpResponseRedirect(
                "{url}/?q={token}".format(
                    url = reverse('accounts_registration_verify'),
                    token = token
                )
            )


    data['form_reg'] = form_reg
    return render(request, 'accounts/registration.html', data)

def registration_closed(request):
    """
    This view is called when user tries to register in case registration is closed via ``settings.REGISTRATION_OPEN``.

    **Authors**: Gagandeep Singh
    """
    data = {}
    return render(request, 'accounts/registration_closed.html', data)

def registration_verify(request):
    """
    A View to verify user registration by entering OTP send to mobile no.

    This view can be called in case:
        - **Normal registration flow**: After user has signed up with his details, he is redirected to this view to verify himself.
        - **Direct call withing expiry**: In case user was unable to finish verification, he can directly use url before this link expires
          according to :class:`accounts.models.RegisteredUser`.``last_reg_date``.

    **Authors**: Gagandeep Singh
    """

    token = request.GET['q']

    # Decode token
    data_token = jwt.decode(token, 'secret')
    new_registered_user = RegisteredUser.objects.get(id=data_token['reg_user_id'])

    # Check expiry
    if (timezone.now() - new_registered_user.last_reg_date).total_seconds() >= settings.VERIFICATION_EXPIRY:
        raise Http404("Link expired! Please register again.")

    data = {
        'token': token,
        'new_registered_user': new_registered_user
    }
    return render(request, 'accounts/registration_verify.html', data)
# ---------- /Registration ----------
