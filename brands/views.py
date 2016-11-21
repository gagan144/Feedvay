# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from brands.forms import *
from brands import operations as ops
from brands.models import Brand, BrandOwner

from utilities.decorators import registered_user_only, brand_console
from utilities.api_utils import ApiResponse

# ==================== Console ====================
@registered_user_only
def console_brands(request):
    """
    View to display all user brands; owned as well as associated.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {}
    return render(request, 'brands/console/my_brands.html', data)

@registered_user_only
def console_create_brand(request):
    """
    View to add new brand. Newely created brand is marked for verification which is then
    published after manual verification.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "app_name": "app_create_brand"
    }
    return render(request, 'brands/console/create_brand.html', data)

@registered_user_only
def console_save_brand(request):
    """
    API view to create or edit a brand. User fills and submits form and depending upon
    whether id is provided or not, brand is either created or updated request is made.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form_brand = BrandCreateEditForm(request.POST, request.FILES)

        if form_brand.is_valid():
            form_data = form_brand.cleaned_data
            brand_id = request.POST.get('id', None)

            if brand_id:
                # Brand edit; Create edit request
                raise NotImplementedError("Brand edit yet to be implemented.")
            else:
                ops.create_new_brand(form_data, request.user.registereduser)
                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Your request has been send for verification.').gen_http_response()
        else:
            errors = dict(form_brand.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@brand_console
def console_brand_settings(request):
    """
    View for brand settings. Only applicable for brand console.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "app_name": "app_brand_settings",
        "list_other_owners": request.curr_brand.owners.all().exclude(user_id=request.user.id).select_related('user')
    }
    return render(request, 'brands/console/brand_settings.html', data)

@registered_user_only
@brand_console
def console_brand_disassociate(request):
    """
    API view to disassociate current user from the brand. Only applicable for brand console.

    **Points**:

        - **Registered user** is obtained from current session.
        - **Brand** is obtained from ``request.curr_brand``.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        brand = request.curr_brand
        reg_user = request.user.registereduser

        confirm = request.POST.get('confirm', False)
        if confirm == 'true':
            try:
                # brand.delete_owner(reg_user)  #TODO: Uncomment
                return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok').gen_http_response()
            except BrandOwner.DoesNotExist:
                # No association found; Invalid request
                return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='You are not associated with this brand.').gen_http_response()
        else:
            # Confirmation missing.
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please confirm your action.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# ==================== /Console ====================
