# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models.query import Q

from django.contrib.auth.models import User
from accounts.models import *

class RegisteredUserInline(admin.StackedInline):
    """
    Admin inline for displaying 'RegistrationUser' details.

    **Authors**: Gagandeep Singh
    """
    model = RegisteredUser
    verbose_name = 'Registration details'
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.registereduser.__class__._meta.fields]
        self.readonly_fields = readonly_fields
        return self.readonly_fields

# ----- User proxy model for registered user ------
class UserProxyForRegUser(User):
    """
    This is a proxy model of :class:`django.contrib.auth.models.User` model to override its behavior for registered user.
    This does not include any users that are not registered (i.e. Staff user etc).

    **Authors**: Gagandeep Singh
    """
    class Meta:
        verbose_name = 'Registered User'
        proxy = True

@admin.register(UserProxyForRegUser)
class RegisteredUserProxyAdmin(admin.ModelAdmin):
    """
    Django admin for 'RegisteredUser'.

    **Authors**: Gagandeep Singh
    """
    fieldsets = (
        (None, {'fields': ('username', ('first_name', 'last_name'), 'email', 'password')}),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active', 'registereduser__status', 'registereduser__reg_method')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    inlines = [RegisteredUserInline]

    # def has_add_permission(self, request):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(RegisteredUserProxyAdmin, self).get_queryset(request)
        return qs.filter(registereduser__isnull=False)


# ---------- Override Django User Admin ----------
class UserAdminOverride(auth_admin.UserAdmin):
    """
    Overriding default django user admin so that only those user are shown who are any of the following:
        - NOT a registered users
        - staff user
        - superuser

    **Authors**: Gagandeep Singh
    """
    def get_queryset(self, request):
        qs = super(UserAdminOverride, self).get_queryset(request)
        return qs.filter(Q(registereduser=None) or (Q(is_staff=True) or Q(is_superuser=True)))
admin.site.unregister(User)
admin.site.register(User, UserAdminOverride)
