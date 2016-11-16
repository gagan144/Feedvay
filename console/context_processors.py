# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from brands.models import Brand, BrandOwner

def console(request):
    """
    Returns all kinds of context variables required by the console app for a logged in registered user.

    **Authors**: Gagandeep Singh
    """

    if request.user.is_authenticated() and request.path.startswith('/console/'):
        reg_user = request.user.registereduser

        return {
            "list_owned_brands": Brand.objects.filter(owners=reg_user).only('brand_uid', 'name', 'logo', 'icon', 'status')
        }
    else:
        return {}