# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import jwt
from django.contrib import auth
import ujson

from django.contrib.auth.models import User

from rest_framework import viewsets, status, response
from utilities.fcm_utils import UserDeviceSerializer

from accounts.forms import *
from accounts.models import *
from accounts.utils import *
from accounts.exceptions import *
from owlery import owls
from utilities.api_utils import ApiResponse
from utilities.decorators import registered_user_only

# ---------- Login ----------
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
        'recovery_failed': bool(request.GET.get('recovery_failed',0)),
        'country_tel_code': country_tel_code
    }

    if request.POST:
        username = request.POST['username']     # Warning: Not actual username
        actual_username = RegisteredUser.construct_username(country_tel_code, username)  # Use this for authentication
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
                # So, Check user password
                if user.check_password(password):
                    # --- Password is valid ---

                    # Perform action based on the user class
                    if user_class == ClassifyRegisteredUser.UNVERIFIED:
                        # --- Unverified user; redirect to verification ---
                        # Create verification code token
                        user_token, is_utoken_new = UserToken.objects.update_or_create(
                            registered_user = registered_user,
                            purpose = UserToken.PUR_REG_VERF,
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
                        data['username'] = actual_username
                        return render(request, 'accounts/account_suspended.html', data)

                    elif user_class == ClassifyRegisteredUser.VERIFIED:
                        # Authenticate user credentials
                        auth_user = auth.authenticate(username=actual_username,password=password)

                        if auth_user:
                            # --- Authentic user; provide session ---
                            auth.login(request, user)

                            # Check for 'Remember Me'
                            if not request.POST.get('remember_me',None):
                                # 'Remember Me' was not selected
                                # Expire session after 'SESSION_COOKIE_AGE' seconds
                                # OR after browser is closed.
                                request.session.set_expiry(0) # Expire when web browser is closed
                            else:
                                # 'Remember Me' was selected
                                # Expires after 'SESSION_COOKIE_AGE_PUBLIC' seconds only
                                # Does not expires on browser close
                                request.session.set_expiry(settings.SESSION_COOKIE_AGE_PUBLIC)

                            next = request.GET.get('next',None)
                            if next and next != '':
                                return HttpResponseRedirect(request.GET['next'])
                            else:
                                return HttpResponseRedirect(reverse('console_home'))

                        else:
                            # --- Invalid password: auth.authenticate() ---
                            data['login_fail'] = True
                            data['username'] = username
                else:
                    # --- Invalid password: user.check_password() ---
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
    return HttpResponseRedirect(reverse('accounts_login'))
# ---------- /Login ----------

# ---------- Registration ----------
def registration(request):
    """
    View to handle registration. If called with GET opens registrations form otherwise on POST
    register a user with given details.

    **Type**: GET/POST

    **Authors**: Gagandeep Singh
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('console_home'))
    if not settings.REGISTRATION_OPEN:
        return HttpResponseRedirect(reverse('accounts_registration_closed'))

    country_tel_code = '+91'    #TODO: Set default country_tel_code
    data = {
        'country_tel_code': country_tel_code,
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY,
        'days': range(1,32),
        'month': range(1,13),
        'year': range(1900, (timezone.now().year+1))
    }
    form_reg = RegistrationForm()

    if request.method.lower() == 'post':
        # Gather form data from POST
        data_reg = request.POST.copy()
        data_reg['country_tel_code'] = country_tel_code
        form_reg = RegistrationForm(data_reg)
        form_reg.is_valid() # BandAid: `form_reg.cleaned_data` throws error if this is not called

        form_data = form_reg.cleaned_data
        username = RegisteredUser.construct_username(country_tel_code, form_data['mobile_no'])

        # Validate form
        if form_reg.is_valid():

            # Classify user and take actions accordingly
            user_class = ClassifyRegisteredUser.classify(username)

            if user_class in [ClassifyRegisteredUser.STAFF, ClassifyRegisteredUser.VERIFIED, ClassifyRegisteredUser.SUSPENDED]:
                # Deny
                data['username_exists'] = True
            elif user_class == ClassifyRegisteredUser.UNVERIFIED:
                # Bypass: Send token & redirect to verification
                # No update of user information here
                registered_user = RegisteredUser.objects.get(user__username=username)

                # If this registered user is a lead, transit its state
                if registered_user.status == RegisteredUser.ST_LEAD:
                    registered_user.trans_registered()
                    registered_user.save()

                with transaction.atomic():
                    # Update last registration date
                    registered_user.last_reg_date = timezone.now()
                    registered_user.save()

                    # Create verification code token
                    user_token, is_utoken_new = UserToken.objects.update_or_create(
                        registered_user = registered_user,
                        purpose = UserToken.PUR_REG_VERF,
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

                    # Create'RegisterUser'
                    new_registered_user = RegisteredUser.objects.create(
                        user = new_user,
                        reg_method = RegisteredUser.REG_WEB_PORTAL
                    )

                    # Set password
                    new_registered_user.set_password(form_data['password'], False) # This will save user

                    # Create 'UserProfile'
                    user_profile = UserProfile(
                        registered_user_id = new_registered_user.id
                    )
                    user_profile.add_update_attribute('first_name', new_user.first_name, auto_save=False)
                    user_profile.add_update_attribute('last_name', new_user.last_name, auto_save=False)
                    user_profile.add_update_attribute('date_of_birth', form_reg.get_date_of_birth(), auto_save=False)
                    user_profile.add_update_attribute('gender', form_data['gender'], auto_save=False)
                    user_profile.save()


                    # Transit status from 'lead' to 'verification_pending'
                    if new_registered_user.status == RegisteredUser.ST_LEAD:
                        new_registered_user.trans_registered()
                        new_registered_user.save()

                    # Create verification code token
                    user_token, is_utoken_new = UserToken.objects.update_or_create(
                        registered_user = new_registered_user,
                        purpose = UserToken.PUR_REG_VERF,
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
    A view to verify user registration by entering verification code that was send to user mobile no.

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
        user_token = UserToken.objects.get(registered_user=new_registered_user, purpose=UserToken.PUR_REG_VERF, expire_on__gt=now)

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
            entered_code = request.POST['code']

            # Verify entered code value
            if entered_code == user_token.value:
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
                    request.session.set_expiry(0) # Expire when web browser is closed

                # Redirect to root page
                return HttpResponseRedirect(reverse('console_home')+"?welcome=true")

            else:
                data['status'] = 'failed'
                data['message'] = 'Code verification failed.'

        return render(request, 'accounts/registration_verify.html', data)

    except UserToken.DoesNotExist:
        raise Http404("Invalid or expired link! Sign in or sign up again to re-initiate activation.")

def registration_resend_code(request):
    """
    View to re-send verification code during registration process.

        - No limitation on number of request is set for now.
        - Call to this view is only valid for registered user who's status is `verification_pending`.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        reg_user_id = request.POST['id']

        try:
            reg_user = RegisteredUser.objects.get(id=reg_user_id, status=RegisteredUser.ST_VERIFICATION_PENDING)

            # Create verification code token
            user_token, is_utoken_new = UserToken.objects.update_or_create(
                registered_user = reg_user,
                purpose = UserToken.PUR_REG_VERF,
                defaults = {
                    "created_on" : timezone.now()
                }
            )

            owls.SmsOwl.send_reg_verification(reg_user.user.username, user_token, reg_user.user.username)

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()

        except RegisteredUser.DoesNotExist:
            return ApiResponse(status=ApiResponse.ST_UNAUTHORIZED, message='Invalid username').gen_http_response()
    else:
        # Forbidden GET
        return HttpResponseForbidden('Forbidden! Use post.')

# ---------- /Registration ----------

# ---------- Password recovery ----------
def reset_password_plea(request):
    """
    A web API view to plea for password reset/recovery. This view verifies the user and
    send password recovery SMS and email containing verification code that will be used to reset password.

    .. note::
        Only 'Verified' and 'Unverified' users can plea for password recovery

    :returns: An json response of type :class:`utilties.api_utils.ApiResponse`.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        country_tel_code = '+91'    #TODO: Set default country_tel_code
        mobile_no = request.POST['username']

        username = RegisteredUser.construct_username(country_tel_code, mobile_no)

        # Classify user
        class_name = ClassifyRegisteredUser.classify(username)

        if class_name in [ClassifyRegisteredUser.UNVERIFIED, ClassifyRegisteredUser.VERIFIED]:
            # Allowed; Send verification code
            # Get RegisteredUser
            registered_user = RegisteredUser.objects.get(user__username=username)

            # Create verification code token
            user_token, is_utoken_new = UserToken.objects.update_or_create(
                registered_user = registered_user,
                purpose = UserToken.PUR_PASS_RESET,
                defaults = {
                    "created_on" : timezone.now()
                }
            )

            # Send owls
            owls.SmsOwl.send_password_reset(
                mobile_no = username,
                user_token = user_token,
                username = username
            )
            if registered_user.user.email and registered_user.user.email != '':
                owls.EmailOwl.send_password_reset(
                    email_address = registered_user.user.email,
                    user_token = user_token,
                    username = username
                )

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Verification code send.').gen_http_response()

        elif class_name == ClassifyRegisteredUser.SUSPENDED:
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Your account has been suspended.').gen_http_response()
        else:
            # New, Staff user
            return ApiResponse(status=ApiResponse.ST_UNAUTHORIZED, message='Invalid account.').gen_http_response()

    else:
        # Incase of GET request
        return ApiResponse(status=ApiResponse.ST_NOT_ALLOWED, message='GET not allowed. Please use POST.').gen_http_response()

def reset_password_plea_verify(request):
    """
    An API view to check 'forgot password' recovery code. This is used to tell user
    if the code he entered matched or not as he completes entering the code.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    country_tel_code = '+91'    #TODO: Set default country_tel_code

    mobile_no = request.GET['username']
    verification_code = request.GET['verification_code']

    actual_username = RegisteredUser.construct_username(country_tel_code, mobile_no)

    try:
        passed = UserToken.verify_user_token(
            username = actual_username,
            purpose = UserToken.PUR_PASS_RESET,
            value = verification_code
        )

        if passed:
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Verification failed.').gen_http_response()

    except InvalidRegisteredUser:
        return ApiResponse(status=ApiResponse.ST_UNAUTHORIZED, message='Invalid account.').gen_http_response()

def recover_account(request):
    """
    A view to recover user account by:

        1. First verifying 'verification code',
        2. Reset password
        3. Logging in the user if user is verified else redirecting for verification. Delete token as well.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        country_tel_code = '+91'    #TODO: Set default country_tel_code

        data_recv = request.POST.copy()
        data_recv['country_tel_code'] = country_tel_code
        form_recover = PasswordResetForm(data_recv)
        form_recover.is_valid() # BandAid: `form_reg.cleaned_data` throws error if this is not called

        form_data = form_recover.cleaned_data
        mobile_no = str(form_data['mobile_no'])
        actual_username = RegisteredUser.construct_username(country_tel_code, mobile_no)

        # Validate form
        if form_recover.is_valid():
            try:
                # (1) Verify token
                passed = UserToken.verify_user_token(
                    username = actual_username,
                    purpose = UserToken.PUR_PASS_RESET,
                    value = form_data['verification_code']
                )

                if passed:
                    # Verification passed
                    user_pass_reset_token = UserToken.objects.get(
                        registered_user = RegisteredUser.objects.get(user__username=actual_username),
                        purpose = UserToken.PUR_PASS_RESET
                    )

                    # (2) Reset password
                    user = User.objects.get(username=actual_username)
                    user.set_password(form_data['new_password'])
                    user.save()

                    # (3) Check user class
                    user_class = ClassifyRegisteredUser.classify(actual_username)

                    if user_class == ClassifyRegisteredUser.VERIFIED:
                        # --- (3.1) Verified user: Log him in ---
                        # Delete Token
                        user_pass_reset_token.delete()

                        # Login user and create session
                        auth.login(request, user)
                        request.session.set_expiry(0) # Expire when web browser is closed

                        # Redirect to home
                        return HttpResponseRedirect(reverse('console_home'))

                    elif user_class == ClassifyRegisteredUser.UNVERIFIED:
                        # --- (3.2) Unverified user; redirect to verification ---
                        # Delete Token
                        user_pass_reset_token.delete()

                        registered_user = user.registereduser

                        # Create verification code token
                        user_reg_token, is_utoken_new = UserToken.objects.update_or_create(
                            registered_user = registered_user,
                            purpose = UserToken.PUR_REG_VERF,
                            defaults = {
                                "created_on" : timezone.now()
                            }
                        )

                        # Send owls
                        owls.SmsOwl.send_reg_verification(
                            mobile_no = actual_username,
                            user_token = user_reg_token,
                            username = actual_username
                        )

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
                    else:
                        raise NotImplementedError("Invalid condition for user class '{}'".format(user_class))



                else:
                    # Token verification failed
                    return HttpResponseRedirect(reverse('accounts_login')+"?username="+mobile_no+"&recovery_failed=1")

            except InvalidRegisteredUser:
                return HttpResponseRedirect(reverse('accounts_login')+"?username="+mobile_no+"&recovery_failed=1")

        else:
            # Invalid form
            return HttpResponseRedirect(reverse('accounts_login')+"?username="+mobile_no+"&recovery_failed=1")

    else:
        # Forbidden GET
        return HttpResponseForbidden('Forbidden! Use post.')

#  ---------- /Password recovery ----------

# ---------- User devices (FCM) ----------
class UserDeviceViewSet(viewsets.ModelViewSet):
    """
    View to register or de-register user device for Google Firebase Cloud Messaging (FCM).

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    queryset = UserDevice.objects.all()
    serializer_class = UserDeviceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            device = UserDevice.objects.get(dev_id=serializer.data["dev_id"])
        except UserDevice.DoesNotExist:
            device = UserDevice(dev_id=serializer.data["dev_id"])
        device.is_active = True
        device.reg_id = serializer.data["reg_id"]
        device.name = serializer.data["name"]
        device.user = User.objects.get(id=serializer.data["user"])
        device.save()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = UserDevice.objects.get(dev_id=kwargs["pk"])
            self.perform_destroy(instance)
            return response.Response(status=status.HTTP_200_OK)
        except UserDevice.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
# ---------- /User devices (FCM) ----------


# ==================== Console ====================
@registered_user_only
def console_account_settings(request):
    """
    A console view to open user settings. This view then calls individual partials for various sections
    under user account settings.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    registered_user = request.user.registereduser
    data = {
        "app_name": "app_account",
        "user_profile": registered_user.profile
    }
    return render(request, 'accounts/console/account_settings.html', data)

@registered_user_only
def console_account_settings_email_change(request):
    """
    An API view to change user email address.

    **Points**:
        1. Delete all previous email verification token if any.
        2. Create email verification token.
        3. Create json-web-token having new email address, registered user id.
        4. Form a verification link
        5. Send email owl to the new email address.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        reg_user = request.user.registereduser
        new_email = request.POST['new_email']

        with transaction.atomic():
            # Delete all previous email verification token
            UserToken.objects.filter(registered_user=reg_user, purpose=UserToken.PUR_EMAIL_VERIF).delete()

            # Create email verification token
            user_token = UserToken.objects.create(
                registered_user = reg_user,
                purpose = UserToken.PUR_EMAIL_VERIF
            )

            # Create json-web-token
            json_web_token = jwt.encode(
                {
                    'reg_user_id': reg_user.id,
                    'new_email': new_email,
                    'user_token_id': user_token.id
                },
                settings.JWT_SECRET_KEY,
                algorithm = settings.JWT_ALOG
            )

            # Create url
            url = "{}{}".format(settings.FEEDVAY_DOMAIN, reverse('accounts_verify_email', args=[json_web_token]))

            # Send email owl
            owls.EmailOwl.send_email_verification(reg_user, user_token, url, new_email)

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


def verify_email(request, web_token):
    """
    View to verify email and update it to the registered user account.

    **Points**:

        - Decode json-web-token to obtain data
        - Verify with UserToken if it is within expiry time
        - Update email for registeredUser
        - Delete user token
        - Log him in and redirect to account settings if already logged in
          Else show success message.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    # Decode web token
    data = jwt.decode(web_token, settings.JWT_SECRET_KEY)
    reg_user = RegisteredUser.objects.get(id=data["reg_user_id"])
    new_email = data['new_email']

    now = timezone.now()
    try:
        # Verify token
        user_token = UserToken.objects.get(registered_user=reg_user, purpose=UserToken.PUR_EMAIL_VERIF, expire_on__gt=now)

        # Update email for RegisteredUser
        profile = reg_user.profile
        profile.add_update_attribute('email', new_email, auto_save=False)
        profile.mark_attribute_verification('email', True, 'User verified email through verification process.', auto_save=False)
        profile.save()

        # Delete user token
        user_token.delete()

        # Return response
        if request.user.is_authenticated():
            # User is already logged in, redirect to accounts settings
            return HttpResponseRedirect(reverse('console_accounts_settings')+"#/profile")
        else:
            country_tel_code = '+91'    #TODO: Set default country_tel_code
            data = {
                "new_email": new_email,
                "username": RegisteredUser.deconstruct_username(country_tel_code, reg_user.user.username)
            }
            return render(request, 'accounts/email_verification_success.html', data)

    except UserToken.DoesNotExist:
        raise Http404("Invalid or expired link! Please login and edit your email again.")


@registered_user_only
def console_password_change(request):
    """
    An API view to change user password. The user fills a form and submit old & new password.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form_chng = PasswordChangeForm(request.POST)

        if form_chng.is_valid():
            form_data = form_chng.cleaned_data

            # Here request.user must be 'RegisteredUser' since view has been protected by the
            # the decorator 'registered_user_only'
            user = request.user
            registered_user = request.user.registereduser

            # Confirm old password
            if user.check_password(form_data['old_password']):
                # Change password
                new_password = form_data['new_password']
                registered_user.set_password(new_password)

                # Prevent portal logout
                auth.update_session_auth_hash(request, user)

                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
            else:
                return ApiResponse(status=ApiResponse.ST_UNAUTHORIZED, message='Invalid password, please try again.').gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Incomplete submission.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
def console_account_settings_basicinfo_update(request):
    """
    An API view to update registered user basic information.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form = BasicInfoForm(request.POST)

        if form.is_valid():
            registered_user = request.user.registereduser

            all_ok, errors = form.save(str(registered_user.profile.pk))
            if all_ok:
                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
            else:
                return ApiResponse(status=ApiResponse.ST_PARTIAL_SUCCESS, message='Success with few ignored errors.', errors=errors).gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Incomplete submission.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
def console_account_settings_privinfo_update(request):
    """
    An API view to update registered user private information.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form = PrivateInfoForm(request.POST)

        if form.is_valid():
            registered_user = request.user.registereduser

            all_ok, errors = form.save(str(registered_user.profile.pk))
            if all_ok:
                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok').gen_http_response()
            else:
                return ApiResponse(status=ApiResponse.ST_PARTIAL_SUCCESS, message='Success with few ignored errors.', errors=errors).gen_http_response()
        else:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Incomplete submission.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# ==================== Console ====================
