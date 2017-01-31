# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from django.contrib.contenttypes.models import ContentType

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    """
    Django admin for :class:`django.contrib.contenttypes.models.ContentType`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('model', 'app_label')
    list_filter = ('app_label', )
    search_fields = ('app_label', 'model')
    list_per_page = 50

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False