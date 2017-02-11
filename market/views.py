# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from accounts.decorators import registered_user_only, organization_console

from market.models import Brand
from market.forms import *
from market import operations as ops

from utilities.api_utils import ApiResponse

# ==================== Console ====================
@registered_user_only
@organization_console(required_perms='market.brand')
def console_brands(request, org):
    """
    View to display all brands in an organization.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    filter_brands = request.permissions['market.brand']['data_access']
    if filter_brands is None:
        list_brands = []
    else:
        filter_brands['organization_id'] = org.id
        list_brands = Brand.objects.filter(**filter_brands).only('id', 'name', 'brand_uid', 'logo', 'icon', 'active', 'created_by', 'created_on').select_related('created_by')

    data = {
        'app_name': 'app_brands',
        'list_brands': list_brands
    }

    return render(request, 'market/console/brands.html', data)


@registered_user_only
@organization_console(required_perms='market.brand.add_brand')
def console_brand_new(request, org):
    """
    View to open form to add new brand.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "app_name": "app_create_brand"
    }
    return render(request, 'market/console/brand_new.html', data)

@registered_user_only
@organization_console(required_perms='market.brand.add_brand')
def console_brand_create(request, org):
    """
    An API view to create a NEW brand. User fills a form and submit data.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form_brand = BrandCreateEditForm(request.POST, request.FILES)

        if form_brand.is_valid():
            form_data = form_brand.cleaned_data

            ops.create_new_brand(form_data, org, request.user.registereduser)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_brand.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# ==================== /Console ====================