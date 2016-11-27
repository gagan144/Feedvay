# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.db import transaction
from django.conf import settings
from django.utils import timezone
import uuid
import os
import copy

from brands.models import Brand, BrandOwner, BrandChangeRequest
from accounts.models import UserClaim
from owlery import owls
from utilities import aws

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
            ui_theme = Brand.generate_uitheme(primary_color)
            # ui_theme = UiTheme(
            #     primary = primary_color,
            #     primary_dark = ColorUtils.scale_hex_color(primary_color, -40),
            #     primary_disabled = ColorUtils.scale_hex_color(primary_color, 60)
            # )
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

def mark_brand_verified(brand, remarks=None):
    """
    Method to mark brand verified. It is assumed here all prerequisites and verification process
    have been completed.

    :param brand: Brand that needs to be verified.
    :param remarks: (optional) Any remarks related to verification. (can be HTML)

    .. note:
        Applicable only for ``verification_pending`` brand only.

    **Authors**: Gagandeep Singh
    """

    # Validate entry point
    if brand.status != Brand.ST_VERF_PENDING:
        raise Exception('This method is only applicable for verification_pending brand.')

    brand.trans_verified(remarks)
    brand.save()

    # Send owls
    owls.SmsOwl.send_brand_verified(brand)
    owls.EmailOwl.send_brand_verified(brand)
    owls.NotificationOwl.send_brand_verified(brand)

def mark_brand_verification_failed(brand, reason):
    """
    Method to mark a brand failed in verification. It is assumed here all checks have been made
    before marking it failed.

    :param brand: Brand that needs to be verified.
    :param reason: Reason for failure. (ca be HTML)
    """

    # Validate entry point
    if brand.status  != Brand.ST_VERF_PENDING:
        raise Exception('This method is only applicable for verification_pending brand.')

    brand.trans_verification_failed(reason)
    brand.save()

    # Send owls



def reregister_or_update_brand(brand, data, files=None):
    """
    Method to revise brand status. A brand can be re-registered after verification failure by providing
    new details or brand information can be updated inplace without logging changes if it is
    still pending for verification.

    :param brand: Brand that needs to be updated.
    :param data: Dictionary of fields-value pair that must be updated.
    :param files: (Optional) Dictionary of files to update logo/icon etc. Usually this is ``request.FILES``.

    **Points**:

        - Files handled: ``file_log``, ``file_icon``

    .. note:
        Only applicable for brand with status ``verification_failed`` or ``verification_pending``.

    **Authors**: Gagandeep Singh
    """

    # Validate entry point
    if brand.status not in [Brand.ST_VERF_PENDING, Brand.ST_VERF_FAILED]:
        raise Exception('This method is only applicable for verification failed/pending brands.')
    if len(data)==0 and (files is None or len(files)==0):
        raise Exception("Please provide data or files that needs to be updated")

    # OK! Now proceed
    # Update all data in the brand
    # Set data fields
    for field, new_val in data.iteritems():
        if field not in ['ui_theme__primary']:
            setattr(brand, field, new_val)

    # Set theme if required
    primary_color = data.get('ui_theme__primary', None)
    if primary_color:
        ui_theme = Brand.generate_uitheme(primary_color)
        brand.ui_theme = ui_theme.to_json()

    # Set media files if any
    if files.get('file_logo', None):
        brand.logo = files['file_logo']
    if files.get('file_icon', None):
        brand.icon = files['file_icon']

    # Make status transition if currently failed
    if brand.status == Brand.ST_VERF_FAILED:
        # Make transition to ``verification_pending``.
        brand.trans_revise_verification()

    # Save brand
    update_theme = True if primary_color else False
    brand.save(update_theme=update_theme)

def create_brand_change_log(brand, reg_user, data, files=None):
    """
    Method to create a change request log for a brand. This method is only applicable for
    ``verified`` brand.

    :param brand: Brand that needs to be updated.
    :param reg_user: Registered User that requested the change.
    :param data: Dictionary of fields-value pair that must be updated.
    :param files: (Optional) Dictionary of files to update logo/icon etc. Usually this is ``request.FILES``.
    :return: (is_valid, errors) errors are returned only if is_valid is False

    **Points**:

        - Files handled: ``file_log``, ``file_icon``


    .. note:
        Only applicable for brand with status ``verified``.

    **Authors**: Gagandeep Singh
    """

    # Validate entry point
    if brand.status != Brand.ST_VERIFIED:
        raise Exception('This method is only applicable for verified brands.')
    if len(data)==0 and (files is None or len(files)==0):
        raise Exception("Please provide data or files that needs to be updated")

    # OK! Now proceed
    data = copy.deepcopy(data)

    is_valid = True
    errors = {}

    file_urls = None
    if len(files):
        file_urls = {}

        # Logo image
        if files.get('file_logo', None):
            file_obj = files['file_logo']

            # validate
            if Brand.validate_logo_image(file_obj):
                id = str(uuid.uuid4())
                fname, ext = os.path.splitext(file_obj.name)
                new_filename = "lg-{}.{}".format(id, ext.replace('.',''))

                upload_path = "brands/{brand_uid}".format(
                    brand_uid = brand.brand_uid,
                )

                url = aws.upload_to_s3(file_obj, new_filename, upload_path)
                file_urls['logo'] = url
            else:
                is_valid = is_valid and False
                errors['file_logo'] = ['Logo must be {}x{} and less than {} KB.'.format(
                    Brand.LOGO_DIM[0],
                    Brand.LOGO_DIM[1],
                    Brand.LOGO_MAX_SIZE/1024
                )]

        # Icon image
        if files.get('file_icon', None):
            file_obj = files['file_icon']

            # validate
            if Brand.validate_icon_image(file_obj):
                id = str(uuid.uuid4())
                fname, ext = os.path.splitext(file_obj.name)
                new_filename = "ic-{}.{}".format(id, ext.replace('.',''))

                upload_path = "brands/{brand_uid}".format(
                    brand_uid = brand.brand_uid,
                )

                url = aws.upload_to_s3(file_obj, new_filename, upload_path)
                file_urls['icon'] = url
            else:
                is_valid = is_valid and False
                errors['file_icon'] =['Icon must be {}x{} and less than {} KB.'.format(
                    Brand.ICON_DIM[0],
                    Brand.ICON_DIM[1],
                    Brand.ICON_MAX_SIZE/1024
                )]

        data['files'] = file_urls

    # Final check
    if is_valid:
        # Create change request entry
        with transaction.atomic():
            # Outdate all previous pending requests
            BrandChangeRequest.objects.filter(brand=brand, status=BrandChangeRequest.ST_NEW).update(
                status = BrandChangeRequest.ST_OUTDATED,
                remarks = 'This request was declined due to new request.',
                modified_on = timezone.now()
            )

            # insert new request
            instance = BrandChangeRequest.objects.create(
                brand = brand,
                registered_user = reg_user,
                data_changes = data
            )

        # Send owls
        owls.EmailOwl.send_brand_change_request(
            brand,
            reg_user,
            instance
        )

        return is_valid, None
    else:
        # Invalid
        return is_valid, errors
