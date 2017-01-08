# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *

class ThemeSkinInline(admin.TabularInline):
    """
    Django admin inline for :class:`form_builder.models.ThemeSkin`.

    **Authors**: Gagandeep Singh
    """
    model = ThemeSkin
    extra = 0
    # min_num = 1
    readonly_fields = ('created_on', 'updated_on')

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Django admin for :class:`form_builder.models.Theme`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('fancy_name', 'code', 'get_skin_count', 'active', 'created_on', 'updated_on')
    list_filter = ('active','created_on')
    search_fields = ('name', 'code')
    readonly_fields = ('created_on', 'updated_on')
    inlines = [ThemeSkinInline]
    list_per_page = 20


class FormQuestionInline(admin.TabularInline):
    """
    Django admin inline for form questions.
    """
    model = FormQuestion
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    """
    Django admin for :class:`form_builder.models.Form`.
    """
    list_display = ('title', 'version', 'theme_skin', 'is_ready', 'created_on', 'updated_on')
    list_filter = ('theme_skin', 'languages', 'created_on')
    search_fields = ('title',)
    filter_horizontal = ('languages',)
    readonly_fields = ('translations', 'version', 'created_on', 'updated_on')
    form = select2_modelform(Form, attrs={'width': '250px'})
    list_per_page = 20
    inlines = [FormQuestionInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        readonly_fields += tuple([field.name for field in self.model._meta.fields if not field.editable])

        return readonly_fields

