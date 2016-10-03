# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from watchdog.models import *

from django.utils import timezone

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('shortened_url', 'server_name', 'class_name', 'message', 'times_seen', 'is_resolved')
    list_filter = ('server_name', 'class_name', 'last_seen_on', 'is_resolved')
    raw_id_fields = ('last_seen_by', 'resolved_by')
    search_fields = ('server_name', 'class_name', 'url')

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

        self.readonly_fields = readonly_fields
        return self.readonly_fields

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