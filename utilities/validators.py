# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
import re

def validate_hex_color(value):
    """
    Method to validate hex color code. A hex color code starts with # followed six
    characters in range 0-9 or A-F.

    :param value: Hex color code string
    :return: (bool) True if color value is valid

    **Authors**: Gagandeep Singh
    """
    return True if re.match('^#[0-9A-F]{6}$', value, re.IGNORECASE) else False
