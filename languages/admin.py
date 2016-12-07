# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from languages.models import *

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """
    Django admin model for :class:`languages.models.Language` model.

    **Authors**: Gagandeep Singh
    """
    list_display = ("name", "name_native", "code", "active", "created_on")
    search_fields = ("name", "code")
    list_filter = ("active", "created_on")
    readonly_fields = ("created_on", "updated_on")
    list_per_page = 20