# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms

from brands.models import Brand
from utilities.validators import *

class BrandCreateEditForm(forms.Form):
    """
    Form to create or edit a brand.
    """

    PUR_CREATE = 'create'
    PUR_EDIT = 'edit'
    CH_PURPOSE = (
        (PUR_CREATE, 'Create'),
        (PUR_EDIT, 'Edit')
    )

    purpose = forms.ChoiceField(required=True, choices=CH_PURPOSE)
    name    = forms.CharField(required=True, max_length=255)
    acronym = forms.CharField(required=False, max_length=10)
    description = forms.CharField(required=True)
    file_logo    = forms.ImageField(required=True)
    file_icon   = forms.ImageField(required=True)

    ui_theme__primary = forms.CharField(required=False, max_length=7)

    def clean(self):
        form_data = self.cleaned_data

        if form_data['purpose'] == BrandCreateEditForm.PUR_CREATE:
            if Brand.does_exists(form_data['name']):
                self._errors["name"] = ["Brand already exists."]


        # validate primary color
        if form_data['ui_theme__primary']:
            if not validate_hex_color(form_data['ui_theme__primary']):
                self._errors["ui_theme__primary"] = ["Invalid color code."]
        return form_data