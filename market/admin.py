# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from market.models import *

@admin.register(RestaurantCuisine)
class RestaurantCuisineAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active', )
    search_fields = ('name', )
    list_per_page = 50

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Django admin class for Brand.

    **Authors**: Gagandeep Singh
    """
    list_display = ('name', 'brand_uid', 'organization', 'active', 'created_by', 'created_on')
    list_filter = ('organization', 'active', 'created_on')
    search_fields = ('name', 'brand_uid')
    raw_id_fields = ('organization', 'created_by')
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('organization', 'brand_uid', 'name', 'slug')
        }),
        ('Settings', {
            'fields': ('description', 'logo', 'icon')
        }),
        ('Customizations', {
            'fields': ('ui_theme', 'theme_file')
        }),
        ('Statuses', {
            'fields': ('active', )
        }),
        ('Miscellaneous', {
            'fields': ('created_by', 'created_on', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        update_theme = False
        if change:
            if form.changed_data.__contains__('ui_theme'):
                update_theme = True
        else:
            obj.created_by = request.user

        obj.save(update_theme=update_theme)


