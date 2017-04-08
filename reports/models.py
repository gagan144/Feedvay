# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
import tinymce.models as tinymce_models
from django.utils import timezone
from jsonobject.exceptions import *
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from clients.models import Organization
from reports.visuals import GraphCharts, GRAPH_CLASS_MAPPING

class GraphDiagram(models57.Model):
    """
    Model to define a chart/graph diagram.

    **Points**:

        - ``form_id``: Is optional for feedback since feedback can have multiple forms. However, this is mandatory
          for other cases.

    **Authors**: Gagandeep Singh
    """
    # --- ENUMS ---
    CT_BSP_FEEDBACK = 'bsp_feedback'
    CH_CONTEXT = (
        (CT_BSP_FEEDBACK, 'BSP Feedback'),
    )

    organization = models.ForeignKey(Organization, db_index=True, help_text='Organization to which this graph belongs.')
    context     = models.CharField(max_length=32, choices=CH_CONTEXT, db_index=True, help_text='Context for which this graph is defined.')
    form_id     = models.ForeignKey('form_builder.Form', null=True, blank=True, db_index=True, help_text='Form for which this graph is defined. Optional in case of feedback.')
    graph_type  = models.CharField(max_length=32, choices=GraphCharts.choices_all, help_text='Type of graph.')

    title       = models.CharField(max_length=1024, help_text='User defined title of the graph.')
    description = tinymce_models.HTMLField(null=True, blank=True, help_text='Description about the graph.')

    graph_definition = models57.JSONField(help_text='Graph definition JSON as per graph definition classes.')
    pin_to_dashboard = models.BooleanField(default=False, db_index=True, help_text='If True, this will be display on corresponding context dashboard.')

    # Misc
    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this brand. This can be a staff or registered user.')
    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def graph(self):
        return GRAPH_CLASS_MAPPING[self.graph_type](self.graph_definition)

    def __unicode__(self):
        return "{} - {}".format(self.context, self.graph_type)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        # Check form_id
        if self.context not in [GraphDiagram.CT_BSP_FEEDBACK] and self.form_id is None:
            raise ValidationError("'form_id' is mandatory for '{}' graph diagram.".format(self.context))

        # Check configuration as per type
        try:
            graph_definition = self.graph
        except (BadValueError, WrappingAttributeError) as ex:
            raise ValidationError(ex.message)

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

