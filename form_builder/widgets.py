# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

class FieldWidgets(object):
    """
    Enum class for widgets for various form fields.

    .. note::
        For widget enum create corresponding field rendering html in theme template

    **Authors**: Gagandeep Singh
    """
    # ---------- Widget enums ----------
    HTML_TEXT = 'html_text'
    HTML_EMAIL = 'html_email'
    HTML_PASSWORD = 'html_password'

    HTML_TEXTAREA = 'html_textarea'

    HTML_NUMBER = 'html_number'
    HTML_NUMBER_DECIMAL = 'html_number_decimal'

    HTML_DATE = 'html_date'
    DATEPICKER_DATE = 'datepicker_date'

    HTML_TIME = 'html_time'
    DATEPICKER_TIME = 'datepicker_time'

    HTML_DATEIME_LOCAL = 'html_datetime_local'
    DATEPICKER_DATETIME = 'datepicker_datetime'

    HTML_RADIO = 'html_radio'
    RADIO_BTNGRP_HORIZONTAL = 'radio_btngrp_horiz'

    HTML_SELECT = 'html_select'
    SELECT2_SINGLE = 'select2_single'

    HTML_CHECKBOX = 'html_checkbox'
    SELECT2_MULTI = 'select2_multi'

    RATING_STARS = 'rating_stars'

    # ---------- Field type choices ----------
    choices_text = (
        (HTML_TEXT,'Basic Text'),
    )

    choices_email = (
        (HTML_EMAIL,'Basic Email'),
    )

    choices_password = (
        (HTML_PASSWORD,'Basic Password'),
    )

    choices_textarea = (
        (HTML_TEXTAREA,'Basic Text Area'),
    )

    choices_number = (
        (HTML_NUMBER,'Basic Number'),
    )

    choices_decimal = (
        (HTML_NUMBER_DECIMAL,'Basic Decimal'),
    )

    choices_date = (
        (HTML_DATE,'Basic Date'),
        (DATEPICKER_DATE, 'Date Picker'),
    )

    choices_time = (
        (HTML_TIME,'Basic Time'),
        (DATEPICKER_TIME, 'Time Picker'),
    )

    choices_datetime = (
        (HTML_DATEIME_LOCAL,'Basic DateTime'),
        (DATEPICKER_DATETIME, 'DateTime Picker'),
    )

    choices_binary = (
        (RADIO_BTNGRP_HORIZONTAL, 'Horizontal Radio Button Group'),
        (HTML_RADIO,'Basic Radio'),
    )

    choices_mcss = (
        (HTML_RADIO,'Basic Radio'),
        (HTML_SELECT, 'Basic Select'),
        (SELECT2_SINGLE, 'Autocomplete Select'),
        (RADIO_BTNGRP_HORIZONTAL, 'Horizontal Radio Button Group'),
    )

    choices_mcms = (
        (HTML_CHECKBOX,'Basic Checkbox'),
        (SELECT2_MULTI, 'Autocomplete Select'),
    )

    choices_rating = (
        (RATING_STARS, 'Stars'),
        (RADIO_BTNGRP_HORIZONTAL, 'Numbers'),
        (HTML_SELECT, 'Basic Select'),
    )

