# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models.query import Q
from easy_select2 import select2_modelform

from django.contrib.auth.models import User
from accounts.models import *

class RegisteredUserInline(admin.StackedInline):
    """
    Admin inline for displaying :class:`accounts.models.RegistrationUser` details.

    **Authors**: Gagandeep Singh
    """
    model = RegisteredUser
    verbose_name = 'Registration details'
    raw_id_fields = ('roles', )
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.registereduser.__class__._meta.fields]
        return readonly_fields

# ----- User proxy model for registered user ------
class UserProxyForRegUser(User):
    """
    This is a proxy model of :class:`django.contrib.auth.models.User` model to override its behavior for registered user.
    This does not include any users that are not registered (i.e. Staff user etc).

    **Authors**: Gagandeep Singh
    """
    class Meta:
        verbose_name = 'RegisteredUser user'
        proxy = True

@admin.register(UserProxyForRegUser)
class RegisteredUserProxyAdmin(admin.ModelAdmin):
    """
    Django admin to manage django user who are registered user. This admin class
    allows to change only those user who are registered users.

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

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'registereduser__status', 'registereduser__reg_method')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    inlines = [RegisteredUserInline]
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.registereduser.status != RegisteredUser.ST_VERIFIED:
                readonly_fields += ('is_active', )

        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(RegisteredUserProxyAdmin, self).get_queryset(request)
        return qs.filter(registereduser__isnull=False)

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    """
    Django admin model to manage RegisteredUser.

    **Authors**: Gagandeep Singh
    """
    fieldsets = (
        (None,
            {'fields': ('id', 'user', 'reg_method')}
        ),
        ('Status', {
            'fields': ('reg_count', 'last_reg_date', 'status')
        }),
        ('Permissions and Roles', {
            'fields': ('roles', )
        }),
        ('Dates', {'fields': ('created_on', 'modified_on')}),
    )

    list_display = ('user', 'reg_method', 'reg_count', 'last_reg_date', 'status', 'created_on')
    list_filter = ('reg_method', 'status', 'last_reg_date', 'created_on')
    search_fields = ('user__username', )
    raw_id_fields = ('user', )
    filter_horizontal = ('roles', )
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.__class__._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    """
    Django admin for :class:`accounts.models.UserToken`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('registered_user', 'purpose', 'expire_on', 'created_on')
    list_filter = ('purpose', 'expire_on', 'created_on')
    search_fields = ('registered_user__user__username', )
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.__class__._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserClaim)
class UserClaimAdmin(admin.ModelAdmin):
    """
    Django admin model for :class:`accounts.models.UserClaim`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('registered_user', 'entity', 'entity_id', 'status', 'created_on')
    list_filter = ('entity', 'status', 'created_on')
    search_fields = ('registered_user__user__username', 'entity')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# --- User permissions, roles and data access
@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """
    Django admin for UserPermission.

    **Authors**: Gagandeep Singh
    """
    list_display = ('registered_user', 'organization', 'permission', 'created_by', 'created_on')
    list_filter = ('organization', 'created_on')
    search_fields = ('registered_user__user__username', 'organization__name', 'permission__codename')
    raw_id_fields = ('registered_user', 'created_by')
    list_per_page = 20

    form = select2_modelform(UserPermission, attrs={'width': '300px'})

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Django admin for Role.

    **Authors**: Gagandeep Singh
    """
    list_display = ('name', 'organization', 'created_by', 'created_on')
    list_filter = ('organization', 'created_on')
    search_fields = ('name', 'organization__name')
    raw_id_fields = ('created_by',)
    filter_horizontal = ('permissions', )
    list_per_page = 20

    form = select2_modelform(Role, attrs={'width': '300px'})

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()

@admin.register(UserDataAccess)
class UserDataAccessAdmin(admin.ModelAdmin):
    """
    Django admin for UserDataAccess.

    **Authors**: Gagandeep Singh
    """
    list_display = ('registered_user', 'content_type', 'organization', 'all_access', 'created_by', 'created_on')
    list_filter = ('all_access', 'organization', 'created_on')
    search_fields = ('registered_user__user__username', 'organization__name', 'content_type__model')
    raw_id_fields = ('registered_user', 'created_by')
    list_per_page = 20

    form = select2_modelform(UserDataAccess, attrs={'width': '300px'})

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()



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

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Django admin for :class:`django.contrib.auth.models.Permission`.
    """
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type', )
    search_fields = ('name', 'content_type__model')
    list_per_page = 50

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------- Override FCM Device admin ----------
from fcm.admin import Device, DeviceAdmin

class UserDeviceAdmin(DeviceAdmin):
    """
    Django admin model for user device.

    **Authors**: Gagandeep Singh
    """
    list_display = ['dev_id', 'user', 'name', 'is_active']
    readonly_fields = ('id', 'dev_id', 'user', 'reg_id', 'name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(Device)
admin.site.register(Device, UserDeviceAdmin)

