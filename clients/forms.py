# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms

from django.contrib.auth.models import Permission

from accounts.models import RegisteredUser, OrganizationRole
from clients.models import Organization, OrganizationMember

class AddInviteMemberForm(forms.Form):
    """
    Form to add/invite a new member in the organization

    **Authors**: Gagandeep Singh
    """
    organization = forms.ModelChoiceField(required=False, queryset=Organization.objects.all())
    country_tel_code = forms.CharField(required=True, max_length=4, min_length=3, widget=forms.HiddenInput(), help_text='Country telephone code.')
    mobile_no   = forms.IntegerField(required=True, min_value=1000000000, max_value=9999999999, help_text='Mobile number as username.')

    email       = forms.EmailField(required=False)
    first_name  = forms.CharField(required=True, max_length=30)
    last_name   = forms.CharField(required=True, max_length=30)
    is_owner    = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
    roles       = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationRole.objects.all())
    permissions = forms.ModelMultipleChoiceField(required=False, queryset=Permission.objects.all())

    def clean(self):
        form_data = self.cleaned_data
        print form_data

        org = form_data['organization']     # This might give exception if organization is not correctly set
        username = RegisteredUser.construct_username(form_data['country_tel_code'], form_data['mobile_no'])

        # Validate username; check if user already a member or not
        if OrganizationMember.objects.filter(organization_id=form_data['organization'].id, registered_user__user__username=username).exists():
            self._errors['mobile_no'] = ['Person is already a member of this organization']

        # Validate
        if form_data['is_owner']:
            form_data['is_superuser'] = True

        if not (form_data['is_owner'] or form_data['is_superuser']):
            if len(form_data['roles']) == 0:
                self._errors['roles'] = ['Please select atleast one role.']

        return form_data

    def save(self):
        print "Saved!"



