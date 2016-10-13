# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings
import jwt
from django.contrib import auth

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
                username = "{}-{}".format(country_tel_code, form_data['mobile_no'])

                # Create 'User' model
                new_user = User(
                    username = username,
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
                new_registered_user.save()

                # Create OTP token
                user_token, is_utoken_new = UserToken.objects.update_or_create(
                    registered_user = new_registered_user,
                    purpose = UserToken.PUR_OTP_VERF,

                    defaults = {
                        "created_on" : timezone.now()
                    }
                )

            # TODO: Send all owls

            # Generate token & redirect to verification
            token = jwt.encode(
                {
                    'reg_user_id': new_registered_user.id,
                    'user_token': user_token.id
                },
                settings.JWT_SECRET_KEY,
                algorithm = settings.JWT_ALOG
            )
            return HttpResponseRedirect(
                "{url}?q={token}".format(
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

    jwtoken = request.POST['q'] if request.method.lower() == 'post' else request.GET['q']

    # Decode token
    data_jwtoken = jwt.decode(jwtoken, settings.JWT_SECRET_KEY)
    new_registered_user = RegisteredUser.objects.get(id=data_jwtoken['reg_user_id'])

    # Check expiry
    if (timezone.now() - new_registered_user.last_reg_date).total_seconds() >= settings.VERIFICATION_EXPIRY:
        raise Http404("Link expired! Please register again.")

    data = {
        'token': jwtoken,
        'new_registered_user': new_registered_user
    }
    if request.method.lower() == 'post':
        entered_otp = request.POST['otp']

        now = timezone.now()
        try:
            user_token = UserToken.objects.get(registered_user=new_registered_user, purpose=UserToken.PUR_OTP_VERF, expire_on__lt=now)

            # Verify otp value
            if entered_otp == user_token.value:
                with transaction.atomic():
                    # Mark user active
                    user = new_registered_user.user
                    user.is_active = True
                    user.save()

                    # Transit 'RegisteredUser' to 'verified'
                    new_registered_user.trans_verification_completed()
                    new_registered_user.save()

                    # Delete UserToken
                    user_token.delete()

                    # Login User
                    user = user
                    backend = auth.get_backends()[0]
                    user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
                    auth.login(request,user)

                    # Redirect to root page
                    return HttpResponseRedirect(reverse('home_user')+"?welcome=true")

            else:
                data['status'] = 'failed'
                data['message'] = 'OTP verification failed.'
        except UserToken.DoesNotExist:
            data['status'] = 'failed'
            data['message'] = 'OTP verification failed.'


    return render(request, 'accounts/registration_verify.html', data)
# ---------- /Registration ----------
