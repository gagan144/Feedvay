# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import JsonResponse

from geography.models import AdministrativeHierarchy, GeoLocation

def geo_location(request):
    """
    Django view to get a GeoLoaction hierarchy tree given a hierarchy

    **Type**: GET

    **Params**:

        - `hier``: specifies hierarchy uid. Default: AdministrativeHierarchy.DEFAULT

    **Authors**: Gagandeep Singh
    """
    hier_uid = request.GET.get('hier', AdministrativeHierarchy.DEFAULT)

    # --- Query --
    result_aggr = GeoLocation._get_collection().aggregate([
        {
            "$match": {
                "hierarchies.hierarchy_uid" : hier_uid
            }
        },
        {
            "$sort": {
                'hierarchies.hierarchy_uid': 1, 'hierarchies.level': 1, 'name': 1
            }
        },
        {
            "$unwind": "$hierarchies"
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "division_type": 1,
                "code_iso": 1,
                "code": 1,
                "hierarchy_uid": "$hierarchies.hierarchy_uid",
                "parent": "$hierarchies.parent",
                "level": "$hierarchies.level",
                "path": "$hierarchies.path",
                "pincode": "$post_office.pincode",
                "office_name": "$post_office.office_name",
                "isLeaf": "$hierarchies.isLeaf",
                "centroid": 1
            }
        }
    ])

    data = []
    for row in result_aggr:
        data.append(row)

    return JsonResponse({
        "objects": data
    })