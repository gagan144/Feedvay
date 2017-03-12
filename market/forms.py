# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django import forms
from mongoengine import *

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
        fields = ['bsp_type', 'schema']


    def clean(self):
        form_data = self.cleaned_data

        # Check if labels are not reserved
        list_reserved_labels = BusinessServicePoint._fields.keys() + MAPPING_BSP_CLASS[form_data['bsp_type']].properties().keys()

        for attr in form_data['schema']:
            attr['label'] = attr['label'].lower()   # Convert labels to lowercase
            if attr['label'] in list_reserved_labels:
                self._errors["schema"] = ["Label '{}' is reserved.".format(attr['label'])]

        return form_data

    def save(self, organization=None, created_by=None):
        if not self.instance.pk:
            self.instance.organization = organization
            self.instance.created_by = created_by
        super(self.__class__, self).save(commit=True)


class BusinessServicePointForm(object):
    """
    Form to create/edit Business or Service Point.

    **Points**:

        - ``errors`` and ``cleaned_data`` are available only after call is ``is_valid()`` method.
        - ``Save()`` method automatically calls ``is_valid()``

    **Authors**: Gagandeep Singh
    """

    exclude = ['id', 'organization_id', 'list_attributes', 'created_by', 'created_on', 'modified_on']

    def __init__(self, data, files=None, instance=None):
        self.data = data
        self.files = files
        self.instance = instance if instance else BusinessServicePoint()
        self.errors = None
        self.cleaned_data = None

    def is_valid(self):
        """
        Method to validate data.
        This also sets ``self.errors`` if any errors are found.

        :return: True if no errors are found else False
        """

        errors = {}
        cleaned_data = {}

        # Loop over all fields
        for fld_name, field in BusinessServicePoint._fields.iteritems():
            # Skip excluded ones
            if fld_name in self.exclude:
                continue

            # Get value
            value = self.data.get(fld_name, None)

            # Is required and None, [], {}
            if field.required and value in [None, [], {}]:
                errors[fld_name] = ["Field required"]
            else:
                # Only if value is not None
                if value is not None:
                    # Check embedded documents & embedded document list
                    has_value_err = False
                    if isinstance(field, EmbeddedDocumentListField):
                        try:
                            value = [ field.field.document_type(**row) for row in value ]
                        except FieldDoesNotExist as ex:
                            errors[fld_name] = [ex.message]
                            has_value_err = True
                    elif isinstance(field, EmbeddedDocumentField):
                        try:
                            value = field.document_type(**value)
                        except FieldDoesNotExist as ex:
                            errors[fld_name] = [ex.message]
                            has_value_err = True

                    # Validate value only if previous error was not found
                    if not has_value_err:
                        try:
                            field._validate(value)
                        except ValidationError as ex:
                            errors[fld_name] = [ex.message]

                cleaned_data[fld_name] = value

        if len(errors):
            # Has errors
            self.errors = errors
            self.cleaned_data = None
            return False
        else:
            # Ok! No errors
            self.errors = None
            self.cleaned_data = cleaned_data
            return True


    def save(self, organization=None, created_by=None):
        """
        Method to save BSP.

        :param organization: Organization instance used only when new instance is being created
        :param created_by: User instance used only when new instance is being created
        :return: :class:`market.models.BusinessServicePoint` instance
        """
        self.is_valid()
        instance = self.instance

        for fld_name, value in self.cleaned_data.iteritems():
            setattr(instance, fld_name, value)

        if instance.pk is None:
            instance.organization_id = organization.id
            instance.created_by = created_by.id

        instance.save()

        return instance




