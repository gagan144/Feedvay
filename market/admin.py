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
