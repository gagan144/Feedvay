# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from brands.models import *

class BrandOwnerInline(admin.TabularInline):
    """
    Django admin inline model for :class:`brands.models.BrandOwner`.

    **Authors**: Gagandeep Singh
    """
    model = BrandOwner
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        return readonly_fields

    def has_add_permission(self, request):
        return False


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Django admin model for :class;`brands.models.Brand`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('name', 'brand_uid', 'status', 'active', 'modified_on')
    list_filter = ('status', 'active', 'created_on')
    raw_id_fields = ('created_by', )
    search_fields = ('name', 'acronym', 'brand_uid')
    list_per_page = 20
    inlines = [BrandOwnerInline]

    fieldsets = (
        (None, {
            'fields': ('brand_uid', 'name', 'slug', 'acronym', 'description')
        }),
        ('Status', {
            'fields': ('status', 'failed_reason', 'staff_remarks', 'active', 'disable_claim')
        }),
        ('Customizations', {
            'fields': ('logo', 'icon', 'ui_theme', 'theme_file')
        }),
        ('Miscellaneous', {
            'fields': ('created_by', 'created_on', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        readonly_fields.append('active')

        if obj:
            if obj.status == Brand.ST_VERF_FAILED:
                readonly_fields.append('failed_reason')
            if obj.status == Brand.ST_VERIFIED:
                readonly_fields.remove('active')

        return readonly_fields

    def save_model(self, request, obj, form, change):
        update_theme = False
        if change:
            if form.changed_data.__contains__('ui_theme'):
                update_theme = True
        else:
            obj.created_by = request.user

        obj.save(update_theme=update_theme)

    def delete_model(self, request, obj):
        obj.trans_delete()
        obj.save()

@admin.register(BrandChangeRequest)
class BrandChangeRequestAdmin(admin.ModelAdmin):
    """
    Django admin model for :class:`brands.models.BrandChangeRequest`.

    **Authors**: Gagandeep Singh
    """
    list_display = ('brand', 'registered_user', 'status', 'created_on')
    list_filter = ('status', 'created_on')
    raw_id_fields = ('brand', 'registered_user')
    search_fields = ('brand__name', 'registered_user__user__username')
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields