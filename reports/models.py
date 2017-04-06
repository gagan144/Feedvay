# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
import tinymce.models as tinymce_models
from django.utils import timezone

from django.contrib.auth.models import User

from clients.models import Organization
from reports.visuals import GraphCharts


class GraphDiagram(models57.Model):
    """
    Model to define a chart/graph diagram.

    **Authors**: Gagandeep Singh
    """
    # --- ENUMS ---
    CT_BSP_FEEDBACK = 'bsp_feedback'
    CH_CONTEXT = (
        (CT_BSP_FEEDBACK, 'BSP Feedback'),
    )

    organization = models.ForeignKey(Organization, db_index=True, help_text='Organization to which this visual belongs.')
    context     = models.CharField(max_length=32, choices=CH_CONTEXT, help_text='Context for which this visual is defined')
    type        = models.CharField(max_length=32, choices=GraphCharts.choices_all, help_text='Type of visual')

    title       = models.CharField(max_length=1024, help_text='Title of the diagram')
    description = tinymce_models.HTMLField(null=True, blank=True, help_text='Description about the diagram.')

    config      = models57.JSONField(help_text='Configuration for the visual diagram.')
    pin_to_dashboard = models.BooleanField(default=False, help_text='If True, this will be display on corresponding context dashboard.')

    # Misc
    created_by  = models.ForeignKey(User, editable=False, related_name='created_by', help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    def __unicode__(self):
        return "{} - {}".format(self.context, self.type)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Check configuration as per type

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

