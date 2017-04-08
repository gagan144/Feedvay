# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib import admin
from easy_select2 import select2_modelform

from reports.models import *

@admin.register(GraphDiagram)
class GraphDiagramAdmin(admin.ModelAdmin):
    """
    Django admin for graph diagrams.

    **Authors**: Gagandeep Singh
    """

    list_display = ('title', 'graph_type', 'organization', 'context', 'form_id', 'created_by', 'created_on')
    search_fields = ('title', )
    list_filter = ('context', 'graph_type', 'created_on')
    raw_id_fields = ('created_by', )
    list_per_page = 20

    form = select2_modelform(GraphDiagram, attrs={'width': '300px'})

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields if not field.editable]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            obj.created_by = request.user

        obj.save()