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
