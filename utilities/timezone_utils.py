# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

def validate_timezone_offset_string(tmzn_str):
    """
    Checks if the given timezone string is in the format ``[+/-]HHMM``.
    :param tmzn_str: Timezone offset string
    :return: True if format is valid else False

    **Authors**: Gagandeep Singh
    """

    is_valid = True
    if len(tmzn_str) != 5:
        is_valid = False
    else:
        sign = tmzn_str[:1]
        hh = int(tmzn_str[1:3])
        mm = int(tmzn_str[3:])

        is_valid = (sign in ['+', '-']) and (0 <= hh <= 24) and (0 <= mm <= 59)

    return is_valid