# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from django.db import transaction

from django.contrib.auth.models import Permission

from accounts.models import RegisteredUser, OrganizationRole, UserPermission
from clients.models import Organization, OrganizationMember
from accounts.utils import get_all_superuser_permission_codenames
from accounts import operations as ops_accounts
from owlery import owls

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


        org = form_data['organization']     # This might give exception if organization is not correctly set
        username = RegisteredUser.construct_username(form_data['country_tel_code'], form_data['mobile_no'])

        # Validate username; check if user already a member or not
        if OrganizationMember.objects.filter(organization_id=form_data['organization'].id, registered_user__user__username=username, deleted=False).exists():
            self._errors['mobile_no'] = ['Person is already a member of this organization']

        # Validate
        if form_data['is_owner']:
            form_data['is_superuser'] = True

        if not (form_data['is_owner'] or form_data['is_superuser']):
            if len(form_data['roles']) == 0:
                self._errors['roles'] = ['Please select atleast one role.']

        # roles
        for role in form_data['roles']:
            if role.organization_id != org.id:
                self._errors['roles'] = ["Invalid role '{}' selected.".format(role.name)]
                break

        # permissions
        list_codenames = get_all_superuser_permission_codenames()
        for perm in form_data['permissions']:
            if perm.codename not in list_codenames:
                self._errors['roles'] = ["Invalid permission '{}' selected.'".format(perm.codename)]
                break

        return form_data

    def save(self, created_by):
        data = self.cleaned_data

        username = RegisteredUser.construct_username(data['country_tel_code'], data['mobile_no'])

        with transaction.atomic():
            reg_user_created = False

            # (a) Check if user exists in the system
            try:
                reg_user = RegisteredUser.objects.get(user__username=username)
            except RegisteredUser.DoesNotExist:
                # Create new user
                reg_user = ops_accounts.create_new_registered_user(
                    username = username,
                    form_data = data,
                    reg_method = RegisteredUser.REG_CAPTURED_LEAD,
                    set_passwd = False
                )
                reg_user_created = True

            # (b) Get or create org member; User might be an ex-member
            org_mem, is_new = OrganizationMember.objects.get_or_create(
                organization = data['organization'],
                registered_user = reg_user,
                defaults = {
                    "is_owner": data['is_owner'],
                    "created_by": created_by
                }
            )

            # If was ex-member
            if not is_new:
                # Revive membership
                org_mem.created_by = created_by
                org_mem.deleted = False
                org_mem.save()

            # (c) Permissions, Roles & Data access
            # Check for superuser
            if data['is_superuser']:
                reg_user.superuser_in.add(data['organization'])
                # No need to create roles & permissions
            else:
                # Create Roles
                for role in data['roles']:
                    reg_user.roles.add(role)

                # Create permissions if selected
                list_permissions = data['permissions']
                if len(list_permissions):
                    list_usr_perm = []
                    for perm in list_permissions:
                        list_usr_perm.append(
                            UserPermission(
                                organization = data['organization'],
                                registered_user = reg_user,
                                permission = perm,
                                created_by = created_by
                            )
                        )
                    UserPermission.objects.bulk_create(list_usr_perm)

            # TODO: Create data access

            reg_user.save()

        # Send Owls
        owls.SmsOwl.send_org_invitation(mobile_no=username, org_mem=org_mem, reg_user_created=reg_user_created, username=username)
        if reg_user.user.email:
            owls.EmailOwl.send_org_invitation(org_mem=org_mem)
        owls.NotificationOwl.send_org_invitation(org_mem=org_mem)
