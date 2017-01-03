# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings

from surveys.models import Survey, SurveyPhase
from form_builder.models import Form, ThemeSkin
from languages.models import Translation

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

class SurveyCreateForm(forms.ModelForm):
    """
    Form to to create a new survey.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        model = Survey
        fields = ['type', 'category', 'title', 'description', 'start_date', 'end_date', 'surveyor_type', 'audience_type']

    def clean(self):
        form_data = self.cleaned_data

        instance = self.instance
        if instance.surveyor_type == Survey.SURVYR_INDIVIDUAL and instance.type != Survey.TYPE_SIMPLE:
            self._errors["type"] = ["You cannot create complex survey."]

        return form_data

    def save(self, created_by, *args, **kwargs):
        with transaction.atomic():
            self.instance.created_by = created_by
            new_survey = super(SurveyCreateForm, self).save(*args, **kwargs)

            if kwargs.get('commit', True):
                # Now create first phase
                if new_survey.type == Survey.TYPE_SIMPLE:
                    form_title = new_survey.title
                elif new_survey.type == Survey.TYPE_COMPLEX:
                    form_title = "{} - Phase 1".format(new_survey.title)

                # Create description translation
                # Since it is mongo, it is not rolled back on failure
                trans_description = Translation.objects.create(
                    is_paragraph = True,
                    sentence = new_survey.description
                )

                # Create form
                form = Form.objects.create(
                    title = form_title,
                    description = str(trans_description.pk),
                    theme_skin = ThemeSkin.objects.get(theme__code=settings.DEFAULT_FORM_THEME['theme_code'], code=settings.DEFAULT_FORM_THEME['skin_code'])
                )

                # Create phase
                phase = SurveyPhase.objects.create(
                    survey = new_survey,
                    form = form,
                    order = 1
                )

        return new_survey