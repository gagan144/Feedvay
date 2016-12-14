# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from surveys.models import *

@admin.register(SurveyTag)
class SurveyTagAdmin(admin.ModelAdmin):
    """
    Django admin model for survey tags.

    **Authors**: Gagandeep Singh
    """

    list_display = ('name', 'created_on')
    search_fields = ('name', )
    list_filter = ('created_on', )
    list_per_page = 40

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    """
    Django admin model for survey category.

    **Authors**: Gagandeep Singh
    """

    list_display = ('name', 'active', 'created_on')
    search_fields = ('name', )
    list_filter = ('active', 'created_on')
    list_per_page = 40

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

class SurveyPhaseInline(admin.TabularInline):
    """
    Inline django admin for survey phase.

    **Authors**: Gagandeep Singh
    """
    model = SurveyPhase
    raw_id_fields = ('form', )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """
    Django admin for survey model.
    """

    list_display = ('survey_uid', 'title', 'type', 'start_date', 'end_date', 'status', 'created_on')
    list_filter = ('type', 'category', 'surveyor_type', 'audience_type', 'status', 'created_on')
    raw_id_fields = ('category', 'brand', 'tags', 'created_by')
    search_fields = ('survey_uid', 'title')
    list_per_page = 20
    inlines = [SurveyPhaseInline]

    fieldsets = (
        (None, {
            'fields': ('type', 'category')
        }),
        ('Basic', {
            'fields': ('survey_uid', 'title', 'description')
        }),
        ('Customizations', {
            'fields': ('tags', 'start_date', 'end_date')
        }),
        ('Surveyor', {
            'fields': ('surveyor_type', 'brand')
        }),
        ('Audience', {
            'fields': ('audience_type', 'audience_filters')
        }),
        ('Status', {
            'fields': ('status', )
        }),
        ('Miscellaneous', {
            'fields': ('qrcode', 'created_by', 'created_on', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        readonly_fields.append('status')
        return readonly_fields

    # def has_add_permission(self, request):    #TODO: uncomment
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False

