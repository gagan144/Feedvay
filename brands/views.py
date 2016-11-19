# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from utilities.decorators import registered_user_only
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
    """

    if request.method.lower() == 'post':
        pass
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

# ==================== /Console ====================
