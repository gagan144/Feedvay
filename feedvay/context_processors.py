# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf import settings

def settings_variables(request):
    """
    Context processor to pass majorly used settings variables to templates.

    **Authors**: Gagandeep Singh
    """
    return {
        "API_GOOGLE_MAP": settings.API_GOOGLE_MAP
    }