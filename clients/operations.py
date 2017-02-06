# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

def update_organization(user, org, data, files=None):
    """
    Method to update organization information.

    :param user: User who has made changes.
    :param org: Organization whos information is changed.
    :param data: Dictionary of fields-value pair that must be updated.
    :param files: (Optional) Dictionary of files to update logo/icon etc. Usually this is ``request.FILES``.

    **Points**:

        - Files handled: ``file_log``, ``file_icon``

    **Authors**: Gagandeep Singh
    """

    # Validate entry point
    if len(data)==0 and (files is None or len(files)==0):
        raise Exception("Please provide data or files that needs to be updated")

    # OK! Now proceed
    # Update all data in the organization
    # Set data fields
    for field, new_val in data.iteritems():
        if field not in ['ui_theme__primary']:
            setattr(org, field, new_val)

    # Set theme if required
    primary_color = data.get('ui_theme__primary', None)
    if primary_color:
        ui_theme = org.generate_uitheme(primary_color)
        org.ui_theme = ui_theme.to_json()

    # Set media files if any
    if files.get('file_logo', None):
        org.logo = files['file_logo']
    if files.get('file_icon', None):
        org.icon = files['file_icon']


    # Save org
    update_theme = True if primary_color else False
    org.save(update_theme=update_theme)