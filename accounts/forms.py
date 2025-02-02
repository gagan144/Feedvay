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

    gender      = forms.ChoiceField(required=True, choices=UserProfile.UserAttributes.CH_GENDER)

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

# ----- Console: Profile -----
class BasicInfoForm(forms.Form):
    """
    Form to change registered user basic information as in page 'Account settings > Profile'.

    **Authors**: Gagandeep Singh
    """
    first_name  = forms.CharField(required=True)
    last_name   = forms.CharField(required=True)
    gender      = forms.ChoiceField(required=True, choices=UserProfile.UserAttributes.CH_GENDER)
    date_of_birth = forms.DateTimeField(required=True)


    def save(self, pk):
        """
        Form method to save all details into :class:`accounts.models.UserProfile` model.

        :param pk: ID of :class:`accounts.models.UserProfile` instance which is to be updated
        :return: Tuple (status, errors) - status: True if there were not errors else False, errors: dict of errors

        **Authors**: Gagandeep Singh
        """

        if not self.is_valid():
            raise Exception("Cannot save! Some form fields are not valid.")

        form_data = self.cleaned_data

        user_profile = UserProfile.objects.with_id(pk)

        errors = {}
        user_profile.add_update_attribute('first_name', form_data['first_name'], auto_save=False)
        user_profile.add_update_attribute('last_name', form_data['last_name'], auto_save=False)
        user_profile.add_update_attribute('gender', form_data['gender'], auto_save=False)
        user_profile.add_update_attribute('date_of_birth', form_data['date_of_birth'], auto_save=False)
        user_profile.save()

        status = False if len(errors) else True
        return (status, errors)


class PrivateInfoForm(forms.Form):
    """
    Form to change registered user private information as in page 'Account settings > Profile'.

    **Authors**: Gagandeep Singh
    """
    blood_group     = forms.ChoiceField(required=False, choices=UserProfile.UserAttributes.CH_BLOOD_GROUP)

    def save(self, pk):
        """
        Form method to save all details into :class:`accounts.models.UserProfile` model.

        :param pk: ID of :class:`accounts.models.UserProfile` instance which is to be updated
        :return: Tuple (status, errors) - status: True if there were not errors else False, errors: dict of errors

        **Authors**: Gagandeep Singh
        """

        if not self.is_valid():
            raise Exception("Cannot save! Some form fields are not valid.")

        form_data = self.cleaned_data

        user_profile = UserProfile.objects.with_id(pk)

        errors = {}
        try:
            blood_group = form_data['blood_group']
            if blood_group:
                user_profile.add_update_attribute('blood_group', form_data['blood_group'], auto_save=False)
            else:
                user_profile.delete_attribute('blood_group', auto_save=False)

        except ValidationError as ex:
            errors['blood_group'] = ex.message

        if len(errors) == 0:
            user_profile.save()

        status = False if len(errors) else True
        return (status, errors)







# ----- /Console: Profile -----


# ----- Console: Roles -----
class OrganizationRoleForm(forms.ModelForm):
    """
    Django form to create or edit organization role.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        model = OrganizationRole
        fields = ['organization', 'name', 'permissions']


    def clean(self):
        form_data = self.cleaned_data

        if self.instance.pk is None:
            if OrganizationRole.objects.filter(organization=form_data['organization'], name=form_data['name']).exists():
                self._errors["name"] = ["Role with name '{}' already exists.".format(form_data['name'])]

        return form_data

    def save(self, created_by=None, commit=True):
        if self.instance.pk is None:
            # New instance; set created_by
            self.instance.created_by = created_by

        super(self.__class__, self).save(commit=commit)
# ----- /Console: Roles -----
