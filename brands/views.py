# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render

from utilities.decorators import registered_user_only

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
# ==================== /Console ====================
