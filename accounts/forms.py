# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from captcha.fields import ReCaptchaField
from datetime import date

from accounts.models import *

class RegistrationForm(forms.Form):
    """
    Form for user registration. This form include basic user details enough to kickstart
    a user account. Nothing more than name, age, dob, gender is asked along with phone number
    as username.

    **Authors**: Gagandeep Singh
    """
    country_tel_code = forms.CharField(required=True, max_length=4, min_length=3, widget=forms.HiddenInput(), help_text='Country telephone code.')
    mobile_no   = forms.IntegerField(required=True, min_value=1000000000, max_value=9999999999, help_text='Mobile number as username.')

    first_name  = forms.CharField(required=True)
    last_name   = forms.CharField(required=True)

    dob_day     = forms.IntegerField(required=True)
    dob_month   = forms.IntegerField(required=True)
    dob_year    = forms.IntegerField(required=True)

    gender      = forms.CharField(required=True)

    password    = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    terms_n_conditions = forms.BooleanField(required=True, label='I agree to terms and conditions.')

    captcha = ReCaptchaField(required=True, attrs={"callback": "callback_recaptcha"})   #WARNING: Callback not working; use custom html

    def clean(self):
        form_data = self.cleaned_data

        try:
            dob = date(form_data['dob_year'], form_data['dob_month'], form_data['dob_day'])
        except ValueError:
            self._errors["birthday"] = ["Invalid birth date."]

        if form_data['password'] != form_data['confirm_password']:
            self._errors["confirm_password"] = ["Password does not match"]
            del form_data['password']
            del form_data['confirm_password']
        return form_data

    def get_date_of_birth(self):
        """
        Returns a datetime (timezone unaware) object with time as 00:00:00.00
        :return: Date of birth datetime object
        """
        from datetime import datetime
        form_data = self.cleaned_data
        return datetime(form_data['dob_year'], form_data['dob_month'], form_data['dob_day']) # Unaware datetime object

class PasswordResetForm(forms.Form):
    """
    Form to reset/recover a user's password without login. The user has been send a verification code,
    using which he can set new new password now.

    **Authors**: Gagandeep Singh
    """
    country_tel_code    = forms.CharField(required=True, max_length=4, min_length=3, widget=forms.HiddenInput(), help_text='Country telephone code.')
    mobile_no           = forms.IntegerField(required=True, min_value=1000000000, max_value=9999999999, help_text='Mobile number as username.')
    verification_code   = forms.CharField(required=True, widget=forms.PasswordInput())
    new_password        = forms.CharField(widget=forms.PasswordInput())
    confirm_new_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        form_data = self.cleaned_data
        if form_data['new_password'] != form_data['confirm_new_password']:
            self._errors["confirm_new_password"] = ["Password does not match"]
            del form_data['password']
            del form_data['confirm_password']
        return form_data

class PasswordChangeForm(forms.Form):
    """
    Form to change user password from account settings (after he has logged in).

    **Authors**: Gagandeep Singh
    """

    old_password    = forms.CharField(widget=forms.PasswordInput())
    new_password    = forms.CharField(widget=forms.PasswordInput())
    confirm_new_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        form_data = self.cleaned_data
        if form_data['new_password'] != form_data['confirm_new_password']:
            self._errors["confirm_new_password"] = ["Password does not match"]
            del form_data['password']
            del form_data['confirm_password']
        return form_data