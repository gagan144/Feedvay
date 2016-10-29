# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from easy_select2 import select2_modelform
from django.utils import timezone

from watchdog.models import *

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    """
    Django admin settings for :model:`watchdog.ErrorLog`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('id', 'shortened_url', 'server_name', 'message', 'times_seen', 'is_resolved', 'last_seen_on')
    list_filter = ('is_resolved', 'server_name', 'class_name', 'last_seen_on')
    raw_id_fields = ('last_seen_by', 'resolved_by')
    search_fields = ('server_name', 'class_name', 'url')
    list_per_page = 20

    fieldsets = (
        ('Error source', {
            'fields': ('server_name', 'url')
        }),
        ('Information', {
            'fields': ('class_name', 'message', 'traceback', 'checksum', 'data')
        }),
        ('Occurrence', {
            'fields': ('times_seen', 'first_seen_on', 'last_seen_on', 'last_seen_by')
        }),
        ('Resolve status', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.__class__._meta.fields]
        if obj is not None:
            if not obj.is_resolved:
                readonly_fields.remove('is_resolved')
        else:
            readonly_fields.remove('is_resolved')

        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            if obj.is_resolved:
                obj.resolved_by = request.user
                obj.resolved_on = timezone.now()
        obj.save()

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    """
    Django admin settings for :model:`watchdog.Suggestion`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('id', 'title', 'url', 'is_duplicate', 'status', 'created_on')
    search_fields = ('url', 'title')
    list_filter = ('platform', 'status', 'created_on')
    raw_id_fields = ('user', )
    list_per_page = 20

    fieldsets = (
        ('System area', {
            'fields': ('platform', 'url')
        }),
        ('Suggestion', {
            'fields': ('title', 'description', 'user')
        }),
        ('For staff use', {
            'fields': ('parent', 'status', 'remarks')
        }),
        ('Miscellaneous', {
            'fields': ('created_on', 'modified_on')
        }),
    )

    form = select2_modelform(Suggestion, attrs={'width': '250px'})

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = [field.name for field in obj.__class__._meta.fields if field.editable==False]
            if obj.parent_id is not None:
                readonly_fields.append('status')
                readonly_fields.append('remarks')
        else:
            readonly_fields = self.readonly_fields
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ReportedProblem)
class ReportedProblemAdmin(admin.ModelAdmin):
    """
    Django admin settings for :model:`watchdog.ReportedProblem`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('id', 'title', 'url', 'is_duplicate', 'status', 'created_on')
    search_fields = ('url', 'title')
    list_filter = ('platform', 'status', 'created_on')
    raw_id_fields = ('user', 'error_log')
    list_per_page = 20

    fieldsets = (
        ('System area', {
            'fields': ('platform', 'url')
        }),
        ('Problem', {
            'fields': ('title', 'description', 'user', 'email_id', 'error_log')
        }),
        ('For staff use', {
            'fields': ('parent', 'status', 'remarks')
        }),
        ('Miscellaneous', {
            'fields': ('created_on', 'modified_on')
        }),
    )

    form = select2_modelform(Suggestion, attrs={'width': '250px'})

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = [field.name for field in obj.__class__._meta.fields if field.editable==False]
            if obj.parent_id is not None:
                readonly_fields.append('status')
                readonly_fields.append('remarks')
        else:
            readonly_fields = self.readonly_fields
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False