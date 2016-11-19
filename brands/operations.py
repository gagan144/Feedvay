# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.db import transaction

from brands.models import Brand, BrandOwner
from accounts.models import UserClaim

from utilities.theme import UiTheme, ColorUtils


def create_new_brand(data, claim_reg_user):
    """
    Method to create a new brand. This method encapsulates entire procedure
    to create a new brand after all details have been validated.

    :param data: Dictionary of validated brand data fill model.
    :param claim_reg_user: Claiming Registered User

    **Authors**: Gagandeep Singh
    """

    with transaction.atomic():
        # (1) Create 'Brand' entry with status 'verification_pending'
        primary_color = data.get('ui_theme__primary', None)
        if primary_color:
            ui_theme = UiTheme(
                primary = primary_color,
                primary_dark = ColorUtils.scale_hex_color(primary_color, -40),
                primary_disabled = ColorUtils.scale_hex_color(primary_color, 60)
            )

        else:
            ui_theme = None

        new_brand = Brand(
            name = data['name'],
            description = data["description"],
            logo = data["file_logo"],
            icon = data["file_icon"],
            ui_theme = ui_theme.to_json(),
            created_by = claim_reg_user.user
        )
        new_brand.save(update_theme=True)

        # (2) Create entry for BrandOwner
        ownership = BrandOwner.objects.create(
            brand = new_brand,
            registered_user = claim_reg_user
        )
