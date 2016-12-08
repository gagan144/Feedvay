# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *

class ThemeSkinInline(admin.TabularInline):
    model = ThemeSkin
    extra = 0
    # min_num = 1
    readonly_fields = ('created_on', 'updated_on')


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('fancy_name', 'code', 'get_skin_count', 'active', 'created_on', 'updated_on')
    list_filter = ('active','created_on')
    search_fields = ('name', 'code')
    readonly_fields = ('created_on', 'updated_on')
    inlines = [ThemeSkinInline]
    list_per_page = 20


class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'theme_skin', 'get_response_count', 'created_on', 'updated_on')
    list_filter = ('theme_skin', 'languages', 'created_on')
    search_fields = ('title',)
    filter_horizontal = ('languages',)
    readonly_fields = ('translations', 'version', 'created_on', 'updated_on')
    form = select2_modelform(Form, attrs={'width': '250px'})
    list_per_page = 20

admin.site.register(Form, FormAdmin)
admin.site.register(Theme, ThemeAdmin)
