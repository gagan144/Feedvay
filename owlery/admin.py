# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from owlery.models import *

@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    """
    Django admin to view SMS messages.

    **Authors**: Gagandeep Singh
    """
    list_display = ('mobile_no', 'type', 'priority', 'status', 'created_on')
    list_filter = ('type', 'priority', 'status', 'created_on')
    search_fields = ('mobile_no', 'username')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.__class__._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    """
    Django admin to view email messages.

    **Authors**: Gagandeep Singh
    """
    list_display = ('email_id', 'subject', 'type', 'priority', 'status', 'created_on')
    list_filter = ('type', 'priority', 'status', 'created_on')
    search_fields = ('email_id', 'subject', 'username')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in obj.__class__._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class NotificationRecipientInline(admin.TabularInline):
    """
    Django admin inline for notification recipients.
    """
    model = NotificationRecipient
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields


@admin.register(NotificationMessage)
class NotificationMessageAdmin(admin.ModelAdmin):
    """
    Django model for notification messages.

    **Authors**: Gagandeep Singh
    """
    list_display = ('id', 'type', 'target', 'transmission', 'recipient_count', 'priority', 'status', 'created_on')
    list_filter = ('target', 'transmission', 'type', 'priority', 'status', 'created_on')
    search_fields = ('title', 'on_click_url')
    list_per_page = 20
    inlines = [NotificationRecipientInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False