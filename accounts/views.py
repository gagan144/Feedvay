# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.db import transaction
from django.conf import settings
import jwt
from django.contrib import auth
import json

from django.contrib.auth.models import User
from accounts.forms import *
from accounts.models import *
from accounts.utilities import *
from owlery import owls

# ----- Login ----
def login(request):
    """
    View to login a valid registered user only.

    **Type**: GET/POST

    **Authors**: Gagandeep Singh
    """
    country_tel_code = '+91'    #TODO: Set default country_tel_code
    data={
        'next': request.GET.get('next',None),
        'username': request.GET.get('username', None),
        'country_tel_code': country_tel_code
    }

    if request.POST:
        username = request.POST['username']     # Warning: Not actual username
        actual_username = "{}-{}".format(country_tel_code, username)    # Use this for authentication
        password = request.POST['password']

        try:
            # Get 'User' instance
            # Note: Here `auth.authenticate()` has not been called since 'inactive & verified' user is suspended user.
            # `auth.authenticate()` returns None if user is inactive.
            user = User.objects.get(username=actual_username)

            try:
                # Get 'RegisteredUser' instance
                registered_user = user.registereduser

                # Classify the user
                user_class = ClassifyRegisteredUser.classify(actual_username)

                # Class 'NEW' & 'STAFF' are unreachable here; already check and handled
                if user_class == ClassifyRegisteredUser.UNVERIFIED:
                    # --- Unverified user; redirect to verification ---
                    # Create OTP token
                    user_token, is_utoken_new = UserToken.objects.update_or_create(
                        registered_user = registered_user,
                        purpose = UserToken.PUR_OTP_VERF,
                        defaults = {
                            "created_on" : timezone.now()
                        }
                    )

                    # Send owls
                    owls.SmsOwl.send_reg_verification(
                        mobile_no = actual_username,
                        user_token = user_token,
                        username = actual_username
                    )
                    # Sens email owl

                    # Generate token & redirect to verification
                    token = jwt.encode(
                        {
                            'reg_user_id': registered_user.id,
                            'is_new': False
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

                elif user_class == ClassifyRegisteredUser.SUSPENDED:
                    # --- User's account suspended; show message ---
                    data['username'] = username
                    return render(request, 'accounts/account_suspended.html', data)

                elif user_class == ClassifyRegisteredUser.VERIFIED:
                    # Authenticate user credentials
                    auth_user = auth.authenticate(username=actual_username,password=password)

                    if auth_user:
                        # --- Authentic user; provide session ---
                        auth.login(request, user)

                        # Check for 'Remember Me'
                        if not request.POST.get('remember_me',None):
                            # 'Remember Me' was not selected, so expire session after browser is closed.
                            request.session.set_expiry(0) # 0: expire when the user's Web browser is closed

                        next = request.GET.get('next',None)
                        if next and next != '':
                            return HttpResponseRedirect(request.GET['next'])
                        else:
                            return HttpResponseRedirect(reverse('home'))

                    else:
                        # --- Invalid password ---
                        data['login_fail'] = True
                        data['username'] = username

            except RegisteredUser.DoesNotExist:
                # --- Staff user; Login not allowed here, use django admin ---
                # Unreachable since country tel code is prefixed to input username
                data['login_fail'] = True
                data['username'] = username
        except User.DoesNotExist:
            # --- New user ---
            data['login_fail'] = True
            data['username'] = username

    return render(request, 'accounts/login.html', data)

def logout(request):
    """
    View to logout a user.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    auth.logout(request)
    return HttpResponseRedirect(reverse('home'))

# ---------- Registration ----------
def registration(request):
    """
    View to handle registration. If called with GET opens registrations form otherwise on POST
    register a user with given details.

    **Type**: GET/POST

    **Authors**: Gagandeep Singh
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
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
        form_reg.is_valid() # BandAid: `form_reg.cleaned_data` throws error if this is not called

        form_data = form_reg.cleaned_data
        username = "{}-{}".format(country_tel_code, form_data['mobile_no'])

        # Validate form
        if form_reg.is_valid():

            # Classify user and take actions accordingly
            user_class = ClassifyRegisteredUser.classify(username)

            if user_class in [ClassifyRegisteredUser.STAFF, ClassifyRegisteredUser.VERIFIED, ClassifyRegisteredUser.SUSPENDED]:
                # Deny
                data['username_exists'] = True
            elif user_class == ClassifyRegisteredUser.UNVERIFIED:
                # Bypass: Send token & redirect to verification
                registered_user = RegisteredUser.objects.get(user__username=username)

                # If this registered user is a lead, transit its state
                if registered_user.status == RegisteredUser.ST_LEAD:
                    registered_user.trans_registered()
                    registered_user.save()

                with transaction.atomic():
                    # Update last registration date
                    registered_user.last_reg_date = timezone.now()
                    registered_user.save()

                    # Create OTP token
                    user_token, is_utoken_new = UserToken.objects.update_or_create(
                        registered_user = registered_user,
                        purpose = UserToken.PUR_OTP_VERF,
                        defaults = {
                            "created_on" : timezone.now()
                        }
                    )

                owls.SmsOwl.send_reg_verification(username, user_token, registered_user.user.username)

                # Generate token & redirect to verification
                token = jwt.encode(
                    {
                        'reg_user_id': registered_user.id,
                        'is_new': False
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

            elif user_class == ClassifyRegisteredUser.NEW:
                # Allow
                # Create all database entries in one atomic process
                with transaction.atomic():
                    # Create 'User' model
                    new_user = User(
                        username = username,
                        first_name = form_data['first_name'],
                        last_name = form_data['last_name'],
                        is_active = False

                    )
                    set_user_password(new_user, form_data['password'], False) # This will save user

                    # Create'RegisterUser'
                    new_registered_user = RegisteredUser.objects.create(
                        user = new_user,
                        reg_method = RegisteredUser.REG_WEB_PORTAL
                    )

                    # Transit status from 'lead' to 'verification_pending'
                    if new_registered_user.status == RegisteredUser.ST_LEAD:
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

                owls.SmsOwl.send_reg_verification(username, user_token, new_user.username)

                # Generate token & redirect to verification
                token = jwt.encode(
                    {
                        'reg_user_id': new_registered_user.id,
                        'is_new': True
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

    **Type**: GET

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

    **Type**: GET/POST

    **Authors**: Gagandeep Singh
    """

    jwtoken = request.POST['token'] if request.method.lower() == 'post' else request.GET['q']

    # Decode token
    data_jwtoken = jwt.decode(jwtoken, settings.JWT_SECRET_KEY)
    new_registered_user = RegisteredUser.objects.get(id=data_jwtoken['reg_user_id'])

    now = timezone.now()
    try:
        user_token = UserToken.objects.get(registered_user=new_registered_user, purpose=UserToken.PUR_OTP_VERF, expire_on__gt=now)

        # Check expiry
        time_lapsed_sec = (timezone.now() - user_token.created_on).total_seconds()
        if time_lapsed_sec >= settings.VERIFICATION_EXPIRY:
            raise Http404("Invalid or expired link! Sign in or sign up again to re-initiate activation.")

        data = {
            'token': jwtoken,
            'new_registered_user': new_registered_user,
            'VERIFICATION_EXPIRY_MIN': (settings.VERIFICATION_EXPIRY/60)
        }

        if request.method.lower() == 'post':
            entered_otp = request.POST['otp']

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
                    # user = user
                    backend = auth.get_backends()[0]
                    user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
                    auth.login(request,user)

                # Redirect to root page
                return HttpResponseRedirect(reverse('home')+"?welcome=true")

            else:
                data['status'] = 'failed'
                data['message'] = 'OTP verification failed.'

        return render(request, 'accounts/registration_verify.html', data)

    except UserToken.DoesNotExist:
        raise Http404("Invalid or expired link! Sign in or sign up again to re-initiate activation.")

def registration_resend_otp(request):
    """
    View to send OTP during verification process. No limitation on number of request is set for now.
    Call to this view is only valid for registered user who's status is `verification_pending`.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        reg_user_id = request.POST['id']

        try:
            reg_user = RegisteredUser.objects.get(id=reg_user_id, status=RegisteredUser.ST_VERIFICATION_PENDING)

            # Create OTP token
            user_token, is_utoken_new = UserToken.objects.update_or_create(
                registered_user = reg_user,
                purpose = UserToken.PUR_OTP_VERF,
                defaults = {
                    "created_on" : timezone.now()
                }
            )

            owls.SmsOwl.send_reg_verification(reg_user.user.username, user_token, reg_user.user.username)

            return HttpResponse(json.dumps({"status":"success"}), content_type='application/json')

        except RegisteredUser.DoesNotExist:
            return HttpResponseForbidden('Request denied.')
    else:
        return HttpResponseForbidden('Use post.')

# ---------- /Registration ----------
