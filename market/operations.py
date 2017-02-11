# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from market.models import Brand
from accounts.models import UserDataAccess

# ---------- Brand ----------
def create_new_brand(data, org, reg_user):
    """
    Method to create a new brand. This method encapsulates entire procedure
    to create a new brand after all details have been validated.

    This also creates or update user data access. Permissions are **not** create/updated since
    it is assumed that user has ``market.brand`` permissions.

    :param data: Dictionary of validated brand data fill model.
    :param org: Organization under which this brand has to be created
    :param reg_user: Registered User who created this brand

    .. warning ::
        **DO NOT** use this method as script of force create on behalf of a user. It assums that
        user has permissions over brand.

    **Authors**: Gagandeep Singh
    """

    with transaction.atomic():
        # (1) Create 'Brand'
        primary_color = data.get('ui_theme__primary', None)
        if primary_color:
            ui_theme = Brand.generate_uitheme(primary_color)
        else:
            ui_theme = None

        new_brand = Brand(
            organization = org,
            name = data['name'],
            description = data["description"],
            logo = data["file_logo"],
            icon = data["file_icon"],
            ui_theme = ui_theme.to_json() if ui_theme else None,
            created_by = reg_user.user
        )
        new_brand.save(update_theme=(True if primary_color else False))

        # (2) Set data access
        # Since user could create brand, it means he already has permissions on brand
        # so, now simply update data access
        content_type = ContentType.objects.get(app_label='market', model='brand')
        try:
            # Get existing UserDataAccess
            uda = UserDataAccess.objects.get(organization_id=org.id, registered_user_id=reg_user.id, content_type_id=content_type.id)

            # Update existing; Skip if has all access
            if not uda.all_access:
                access_filter = uda.access_filter

                # Update filter only if it is None or already has "id__in" key
                if access_filter.has_key('id__in') or access_filter is None:
                    # Create or append
                    access_filter["id__in"].append(new_brand.id)
                    uda.access_filter = access_filter
                    uda.save()

        except UserDataAccess.DoesNotExist:
            # Create new
            UserDataAccess.objects.create(
                organization = org,
                registered_user = reg_user,
                content_type = content_type,
                access_filter = {"id__in":[new_brand.id]},
                created_by = reg_user.user,
            )




# ---------- Brand ----------