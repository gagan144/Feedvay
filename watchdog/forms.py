# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms

class ReportedProblemForm(forms.Form):
    """
    Form to capture new problem as reported by the user.

    **Authors**: Gagandeep Singh
    """
    platform = forms.CharField(required=True)
    current_page = forms.CharField(required=True, help_text='yes/no: Is problem in context to current page')
    url = forms.CharField(required=True)
    title = forms.CharField(max_length=512, required=False)
    description = forms.CharField(required=True)

    def clean(self):
        form_data = super(ReportedProblemForm, self).clean()
        if form_data['current_page'] != 'yes':
            if form_data['title'] in [None, '']:
                self._errors["title"] = ["Please provide a title for the problem."]
        return form_data

