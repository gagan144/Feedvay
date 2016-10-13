# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from captcha.fields import ReCaptchaField

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
    middle_name = forms.CharField(required=False)
    last_name   = forms.CharField(required=True)

    password    = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    terms_n_conditions = forms.BooleanField(required=True, label='I agree to terms and conditions.')

    captcha = ReCaptchaField(required=True)

    def clean(self):
        form_data = self.cleaned_data
        if form_data['password'] != form_data['confirm_password']:
            self._errors["confirm_password"] = ["Password does not match"]
            del form_data['password']
            del form_data['confirm_password']
        return form_data
