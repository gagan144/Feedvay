# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from django.core.exceptions import ValidationError

from surveys.models import Survey

class SurveyEditForm(forms.ModelForm):
    """
    Form to to edit an existing survey.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        model = Survey
        fields = ['type', 'category', 'title', 'description', 'start_date', 'end_date', 'audience_type']

    def clean(self):
        form_data = self.cleaned_data

        instance = self.instance
        if instance.pk is None:
            raise ValidationError("You cannot create a new instance while editing a survey.")

        if instance.surveyor_type == Survey.SURVYR_INDIVIDUAL and self.changed_data.__contains__('type'):
            self._errors["type"] = ["You cannot change survey type since it belongs to an individual."]

        return form_data

