# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.utils import timezone

from jsonobject import *

from utilities.validators import validate_hex_color

class UiTheme(JsonObject):
    """
    Json wrapper class to define an UI theme.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    primary     = StringProperty(required=True)
    primary_dark = StringProperty(required=True)
    primary_disabled = StringProperty(required=True)


def render_skin(custom, clr_primary, clr_prim_hover, clr_prim_disabled):
    """
    Method to render theme file with given parameters. This methods renders
    '/templates/theme/inspinia-style-template.css' theme templates using the
    parameters and return string content of the file.

    :param custom: (bool) False if render for Feedvay else True
    :param clr_primary: Main primary color
    :param clr_prim_hover: Darker color of primary used for mouse hover
    :param clr_prim_disabled: Transparent color of primary used for disabled components
    :return: Content of theme file (String)

    **Authors**: Gagandeep Singh
    """
    data = {
        "custom": custom,
        "dated": timezone.now(),
        "PRIMARY": clr_primary,
        "PRIMARY_HOVER": clr_prim_hover,
        "PRIMARY_DISABLED": clr_prim_disabled
    }
    return render_to_response('theme/inspinia-style-template.css', data).content


class ColorUtils:
    """
    Utility class for color manipulation.

    **Authors**: Gagandeep Singh
    """

    @staticmethod
    def cvt_hex_rgb(hex_color):
        """
        Method to convert a hex color value into rgb list.

        :param hex_color: Hex color string of form '#123456'.
        :return: List [<R>, <G>, <B>]

        Throws error if hex color code is invalid.

        **Authors**: Gagandeep Singh
        """

        if not validate_hex_color(hex_color):
            raise Exception("Invalid hex color code.")

        rgb = [ int(hex_color[x:x+2], 16) for x in [1, 3, 5]]   # 0th char is '#'

        return rgb

    @staticmethod
    def scale_rgb_color(rgb, value):
        """
        Method to absolute scale a rgb color by given value.

        :param rgb: List [<R>, <G>, <B>]
        :param value: Positive/Negative value by which color has to be scaled.
        :return: List [<R>, <G>, <B>]

        **Authors**: Gagandeep Singh
        """

        new_rgb = [ min(max(0, c+value), 255) for c in rgb]
        return new_rgb

    @staticmethod
    def cvt_rgb_hex(rgb):
        """
        Method to convert rgb list to hex color code.

        :param rgb: List [<R>, <G>, <B>]
        :return: Hex color code. of form #123456.
        """
        return '#%02x%02x%02x' % tuple(rgb)

    @staticmethod
    def scale_hex_color(hex_color, value):
        """
        Method to absolute scale a hex color by given value.

        :param hex_color: Hex color string of form '#123456'.
        :param value: Positive/Negative value by which color has to be scaled.
        :return: Hex color string of form '#123456'.

        **Authors**: Gagandeep Singh
        """

        # (1) Convert to rgb
        rgb = ColorUtils.cvt_hex_rgb(hex_color)

        # (2) Scale rgb
        new_rgb = ColorUtils.scale_rgb_color(rgb, value)

        # (3) Convert back to hex
        new_hex_color = ColorUtils.cvt_rgb_hex(new_rgb)

        return new_hex_color
