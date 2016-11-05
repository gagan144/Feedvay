# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.utils import timezone

def render_skin(custom, clr_primary, clr_prim_hover, clr_prim_disabled):
    """
    Method to render theme file with given parameters. This methods renders
    '/templates/theme/inspinia-style-template.css' theme templates using the
    parameters and return string content of the file.

    :param custom: False if render for Feedvay else True
    :param clr_primary: Main primary color
    :param clr_prim_hover: Darker color of primary used for mouse hover
    :param clr_prim_disabled: Transparent color of primary used for disabled components
    :return: Content of theme file (String)


    """
    data = {
        "custom": custom,
        "dated": timezone.now(),
        "PRIMARY": clr_primary,
        "PRIMARY_HOVER": clr_prim_hover,
        "PRIMARY_DISABLED": clr_prim_disabled
    }
    return render_to_response('theme/inspinia-style-template.css', data).content