# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http import JsonResponse
import re

from geography.models import AdministrativeHierarchy, GeoLocation
from utilities.api_utils import ApiResponse

def geolocation_tree(request):
    """
    Django view to get a GeoLoaction hierarchy tree given a hierarchy

    **Type**: GET

    **Params**:

        - **hier**: specifies hierarchy uid. Default: AdministrativeHierarchy.DEFAULT

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


def search_geolocation(request):
    """
    API django view to search a location which returns list of possible suggestions.

    **Type**: GET

    **Params**:

        - **q**: Search text of location name
        - **hier**: specifies hierarchy uid. Default: AdministrativeHierarchy.DEFAULT
        - **type**: Division type as per :class:`geography.models.DivisionType`
        - **limit**: No of records to return. Default 10 (max 20)
    """
    # Gather request parameters
    try:
        name = request.GET['q']
        hier_uid = request.GET.get('hier', AdministrativeHierarchy.DEFAULT)
        division_type = request.GET['type']
        limit = min(20, int(request.GET.get('limit', 10)))

        # Validate
        if len(name) < 3:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message="Search text 'q' must be atleast 3 characters long.").gen_http_response()

        # Query database
        result_aggr = GeoLocation._get_collection().aggregate([
            {
                "$match": {
                    "hierarchies.hierarchy_uid" : hier_uid,
                    "division_type": division_type,
                    "name": re.compile(name, re.IGNORECASE)
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
                "$limit": limit
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
                    "full_address": "$hierarchies.full_address",
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

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message="ok", objects=data).gen_http_response()

    except KeyError:
        return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Missing parameters.').gen_http_response()
