# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from geography.utils import *

def update_full_address(queryset):
    """
    Method to iterate over GeoLocation queryset and update full_address for each hierarchy.

    :param queryset: GeoLocation queryset
    :return: Count updated
    """

    count = 0
    for geoloc in queryset:
        # Iterate over hierarchies
        for hier in geoloc.hierarchies:
            full_addr = generate_fulladdr_from_path(hier.path)
            hier.full_address = full_addr

        geoloc.save()
        count += 1

    return count


