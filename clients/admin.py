# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from clients.models import *

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Django admin class for Organization.

    **Authors**: Gagandeep Singh
    """
    list_display = ('name', 'org_uid', 'type', 'status', 'created_by', 'created_on')
    list_filter = ('type', 'status', 'created_on')
    search_fields = ('name', 'org_uid', 'acronym')
    raw_id_fields = ('created_by', )
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('org_uid', 'name', 'acronym', 'slug')
        }),
        ('Settings', {
            'fields': ('description', 'type', 'logo', 'icon')
        }),
        ('Customizations', {
            'fields': ('ui_theme', 'theme_file')
        }),
        ('Statuses', {
            'fields': ('status', 'failed_reason', 'disable_claim')
        }),
        ('Other', {
            'fields': ('staff_remarks', )
        }),
        ('Miscellaneous', {
            'fields': ('created_by', 'created_on', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]

        if obj:
            if obj.status == Organization.ST_VERF_FAILED:
                readonly_fields.append('failed_reason')

        return readonly_fields

    def save_model(self, request, obj, form, change):
        update_theme = False
        if change:
            if form.changed_data.__contains__('ui_theme'):
                update_theme = True
        else:
            obj.created_by = request.user

        obj.save(update_theme=update_theme)

    def delete_model(self, request, obj):
        obj.trans_delete()
        obj.save()


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """
    Django admin class for OrganizationMember.

    **Authors**: Gagandeep Singh
    """
    list_display = ('registered_user', 'organization', 'is_owner', 'deleted', 'created_on')
    list_filter = ('organization', 'is_owner', 'deleted', 'created_on')
    search_fields = ('registered_user__user__username', )
    raw_id_fields = ('registered_user', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = [field.name for field in self.model._meta.fields]
        else:
            readonly_fields = ['deleted', 'created_on', 'modified_on']
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(OrgInvitation)
class OrgInvitationAdmin(admin.ModelAdmin):
    """
    Django admin class for OrgInvitation.

    **Authors**: Gagandeep Singh
    """
    list_display = ('invitee', 'inviter', 'organization', 'org_hier_link', 'status', 'created_on')
    list_filter = ('organization', 'org_hier_link', 'status', 'created_on')
    search_fields = ('invitee__user__username', 'inviter__user__username')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
