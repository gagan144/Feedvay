# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from owlery.models import *

@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    """
    Django admin to view SMS messages.
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