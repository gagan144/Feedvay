# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms

from utilities.validators import *

class BrandCreateEditForm(forms.Form):
    """
    Form to create or edit a brand.
    """
    name    = forms.CharField(required=True, max_length=255)
    description = forms.CharField(required=True)
    file_logo    = forms.ImageField(required=True)
    file_icon   = forms.ImageField(required=True)

    ui_theme__primary = forms.CharField(required=True, max_length=7)

    def clean(self):
        form_data = self.cleaned_data

        # validate primary color
        if form_data['ui_theme__primary']:
            if not validate_hex_color(form_data['ui_theme__primary']):
                self._errors["ui_theme__primary"] = ["Invalid color code."]
        return form_data