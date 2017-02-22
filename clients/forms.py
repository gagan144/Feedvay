# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from django.db import transaction

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import RegisteredUser, OrganizationRole, UserPermission, UserDataAccess
from clients.models import Organization, OrganizationMember
from accounts.utils import get_all_superuser_permission_codenames, get_superuser_perm_json
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
            set_content_type_codes = set()

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

                su_keys = get_superuser_perm_json().keys()
                for k in su_keys:
                    set_content_type_codes.add(k)

            else:
                # Create Roles
                for role in data['roles']:
                    reg_user.roles.add(role)

                    for p in role.permissions.all():
                        set_content_type_codes.add("{}.{}".format(p.content_type.app_label, p.content_type.model))


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

                        set_content_type_codes.add("{}.{}".format(perm.content_type.app_label, perm.content_type.model))

                    UserPermission.objects.bulk_create(list_usr_perm)

            reg_user.save()

            # (d) Create data access
            list_da = []
            cache_ct = {}
            for app_model in set_content_type_codes:
                ct = cache_ct.get(app_model, None)
                if ct is None:
                    _key = app_model.split('.')
                    ct = ContentType.objects.get(app_label=_key[0], model=_key[1])
                    cache_ct[app_model] = ct

                list_da.append(
                    UserDataAccess(
                        organization = data['organization'],
                        registered_user = reg_user,
                        content_type = ct,
                        all_access = True,
                        access_filter = None,
                        created_by = created_by
                    )
                )
            UserDataAccess.objects.bulk_create(list_da)


        # Send Owls
        owls.SmsOwl.send_org_invitation(mobile_no=username, org_mem=org_mem, reg_user_created=reg_user_created, username=username)
        if reg_user.user.email:
            owls.EmailOwl.send_org_invitation(org_mem=org_mem)
        owls.NotificationOwl.send_org_invitation(org_mem=org_mem)

class EditMemberForm(forms.Form):
    """
    Django form to edit membership of a user in an organization..

    **Authors**: Gagandeep Singh
    """
    org_mem     = forms.ModelChoiceField(queryset=OrganizationMember.objects.all())

    is_owner    = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
    roles       = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationRole.objects.all())
    permissions = forms.ModelMultipleChoiceField(required=False, queryset=Permission.objects.all())

    def clean(self):
        form_data = self.cleaned_data

        org_mem = form_data['org_mem']
        org = org_mem.organization

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
        org_mem = data['org_mem']
        org = org_mem.organization
        reg_user = org_mem.registered_user

        with transaction.atomic():
            set_content_type_new_codes = set()  # List of '<app>.<model>' codes

            # Owner
            org_mem.is_owner = data['is_owner']
            org_mem.save()

            # Superuser
            is_su = reg_user.superuser_in.filter(id=org.id).exists()
            if is_su and data['is_superuser'] == False:
                # Was su, now he is NOT
                reg_user.superuser_in.remove(org)
            elif is_su == False and data['is_superuser']:
                # Was NOT su but now he is
                reg_user.superuser_in.add(org)

            # Roles
            list_roles_curr = set(list(reg_user.roles.filter(organization_id=org.id).values_list('id', flat=True)))     # Eg: [1,2,3]
            list_roles_new = set([r.id for r in data['roles']])     # Eg: [1,2,5,6]

            list_roles_rm = list(list_roles_curr-list_roles_new)    # Eg: [1,2,3]-[1,2,5,6] = [3]
            list_roles_add = list(list_roles_new-list_roles_curr)   # Eg: [1,2,5,6]-[1,2,3] = [5,6]

            reg_user.roles.remove(*list_roles_rm)
            reg_user.roles.add(*list_roles_add)

            for role in data['roles']:
                if role.id in list_roles_add:
                    for p in role.permissions.all():
                        set_content_type_new_codes.add("{}.{}".format(p.content_type.app_label, p.content_type.model))

            # Permissions
            list_perms_curr = set(list(UserPermission.objects.filter(organization_id=org.id, registered_user_id=reg_user.id).values_list('permission', flat=True)))
            list_perm_new = set([p.id for p in data['permissions']])

            list_perm_rm = list(list_perms_curr-list_perm_new)
            list_perm_add = list(list_perm_new-list_perms_curr)

            if len(list_perm_rm):
                UserPermission.objects.filter(organization_id=org.id, registered_user_id=reg_user.id, permission_id__in=list_perm_rm).delete()

            bulk_usr_perm = []
            for pid in list_perm_add:
                bulk_usr_perm.append(
                    UserPermission(
                        organization = org,
                        registered_user = reg_user,
                        permission_id = pid,
                        created_by = created_by
                    )
                )
            UserPermission.objects.bulk_create(bulk_usr_perm)

            for p in data['permissions']:
                if p.id in list_perm_add:
                    set_content_type_new_codes.add("{}.{}".format(p.content_type.app_label, p.content_type.model))

            # Data Access; Create only those which do not exists. Ignore present ones
            list_da = []
            cache_ct = {}
            for app_model in set_content_type_new_codes:
                ct = cache_ct.get(app_model, None)
                if ct is None:
                    _key = app_model.split('.')
                    ct = ContentType.objects.get(app_label=_key[0], model=_key[1])
                    cache_ct[app_model] = ct

                if not UserDataAccess.objects.filter(organization_id=org.id, registered_user_id=reg_user.id, content_type_id=ct.id).exists():
                    list_da.append(
                        UserDataAccess(
                            organization = org,
                            registered_user = reg_user,
                            content_type = ct,
                            all_access = True,
                            access_filter = None,
                            created_by = created_by
                        )
                    )

            UserDataAccess.objects.bulk_create(list_da)

