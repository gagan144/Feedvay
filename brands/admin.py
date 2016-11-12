# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin

from brands.models import *

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand_uid', 'status', 'active', 'deleted', 'modified_on')
    list_filter = ('status', 'active', 'deleted', 'created_on')
    raw_id_fields = ('created_by', )
    search_fields = ('name', 'brand_uid')
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('brand_uid', 'name', 'description')
        }),
        ('Status', {
            'fields': ('status', 'failed_reason', 'active', 'deleted', 'disable_claim')
        }),
        ('Miscellaneous', {
            'fields': ('created_by', 'created_on', 'modified_on')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        readonly_fields.append('deleted')
        readonly_fields.append('active')

        if obj:
            if obj.status == Brand.ST_VERF_FAILED:
                readonly_fields.append('failed_reason')
            if obj.status == Brand.ST_VERIFIED:
                readonly_fields.remove('active')

        return readonly_fields

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.save()
