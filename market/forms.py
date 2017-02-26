# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms

from market.models import Brand, BspTypeCustomization, BusinessServicePoint
from market.bsp_types import *
from utilities.validators import *

class BrandCreateForm(forms.Form):
    """
    Form to create new brand.

    **Authors**: Gagandeep Singh
    """
    name    = forms.CharField(required=True, max_length=255)
    # acronym = forms.CharField(required=False, max_length=10)
    description = forms.CharField(required=True)
    file_logo    = forms.ImageField(required=True)
    file_icon   = forms.ImageField(required=True)

    ui_theme__primary = forms.CharField(required=False, max_length=7)

    def clean(self):
        form_data = self.cleaned_data

        if Brand.does_exists(form_data['name']):
            self._errors["name"] = ["Brand already exists."]

        # validate logo & icon
        if not Brand.validate_logo_image(form_data['file_logo']):
            self._errors['file_logo'] = [
                'Logo must be {}x{} and less than {} KB.'.format(
                    Brand.LOGO_DIM[0],
                    Brand.LOGO_DIM[1],
                    Brand.LOGO_MAX_SIZE/1024
                )
            ]

        if not Brand.validate_icon_image(form_data['file_icon']):
            self._errors['file_icon'] = [
                'Icon must be {}x{} and less than {} KB.'.format(
                    Brand.ICON_DIM[0],
                    Brand.ICON_DIM[1],
                    Brand.ICON_MAX_SIZE/1024
                )
            ]

        # validate primary color
        if form_data['ui_theme__primary']:
            if not validate_hex_color(form_data['ui_theme__primary']):
                self._errors["ui_theme__primary"] = ["Invalid color code."]
        return form_data

class BrandEditForm(forms.Form):
    """
    Form to edit a brand.

    **Authors**: Gagandeep Singh
    """
    brand_uid = forms.CharField(required=True)
    name    = forms.CharField(required=True, max_length=255)
    description = forms.CharField(required=True)
    file_logo    = forms.ImageField(required=False)
    file_icon   = forms.ImageField(required=False)

    ui_theme__primary = forms.CharField(required=False, max_length=7)
    active = forms.BooleanField(required=False)

    def clean(self):
        form_data = self.cleaned_data

        try:
            brand = Brand.objects.get(brand_uid=form_data['brand_uid'])

            # Validate logo & icon
            if form_data['file_logo']:
                if not Brand.validate_logo_image(form_data['file_logo']):
                    self._errors['file_logo'] = [
                        'Logo must be {}x{} and less than {} KB.'.format(
                            Brand.LOGO_DIM[0],
                            Brand.LOGO_DIM[1],
                            Brand.LOGO_MAX_SIZE/1024
                        )
                    ]

            if form_data['file_icon']:
                if not Brand.validate_icon_image(form_data['file_icon']):
                    self._errors['file_icon'] = [
                        'Icon must be {}x{} and less than {} KB.'.format(
                            Brand.ICON_DIM[0],
                            Brand.ICON_DIM[1],
                            Brand.ICON_MAX_SIZE/1024
                        )
                    ]


            # Validate primary color
            if form_data['ui_theme__primary']:
                if not validate_hex_color(form_data['ui_theme__primary']):
                    self._errors["ui_theme__primary"] = ["Invalid color code."]

        except Brand.DoesNotExist:
            self._errors["id"] = ["Invalid brand id or brand does not exists."]

        return form_data

    def save(self):
        form_data = self.cleaned_data

        brand = Brand.objects.get(brand_uid=form_data['brand_uid'])

        brand.name = form_data['name']
        brand.description = form_data['description']
        brand.active = form_data['active']

        if form_data['file_logo']:
            brand.logo = form_data['file_logo']

        if form_data['file_icon']:
            brand.icon = form_data['file_icon']

        update_theme = False
        if form_data['ui_theme__primary']:
            brand.ui_theme = Brand.generate_uitheme(form_data['ui_theme__primary'])
            update_theme = True

        brand.save(update_theme=update_theme)

class BspTypeCustomizationForm(forms.ModelForm):
    """
    Form to create/edit BSP customization.

    **Authors**: Gagandeep Singh
    """
    class Meta:
        model = BspTypeCustomization
        fields = ['organization', 'bsp_type', 'schema']


    def clean(self):
        form_data = self.cleaned_data

        # Check if labels are not reserved
        list_reserved_labels = BusinessServicePoint._fields.keys() + MAPPING_BSP_CLASS[form_data['bsp_type']].properties().keys()

        for attr in form_data['schema']:
            if attr['label'] in list_reserved_labels:
                self._errors["schema"] = ["Label '{}' is reserved.".format(attr['label'])]

        return form_data

    def save(self, created_by):
        if not self.instance.pk:
            self.instance.created_by = created_by
        super(self.__class__, self).save(commit=True)


