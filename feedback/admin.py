# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from feedback.models import *
from form_builder.admin import FormAdmin

@admin.register(BspFeedbackForm)
class BspFeedbackFormAdmin(FormAdmin):
    """
    Django admin class for BspFeedbackForm.

    **Authors**: Gagandeep Singh
    """
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BspFeedbackAssociation)
class BspFeedbackAssociationAdmin(admin.ModelAdmin):
    """
    Django admin clas for BspFeedbackAssociation.

    **Authors**: Gagandeep Singh
    """
    list_display = ('form', 'bsp_id')
    search_fields = ('form__name', 'bsp_id')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        readonly_fields += tuple([field.name for field in self.model._meta.fields if not field.editable])

        return readonly_fields
