# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from reports.models import GraphDiagram
from accounts.decorators import registered_user_only, organization_console
from utilities.api_utils import ApiResponse

# ==================== Console ====================

# ==================== /Console ====================

def parse_graph_filters(get_params):
    """
    Method to parse filters for graph data from request.

    :return: JSON dict

    **Authors**: Gagandeep Singh
    """
    filters = {}

    start_date = get_params.get('start_date', None)
    if start_date:
        filters['response_date'] = {
            "$gte": timezone.datetime.strptime(start_date, "%Y-%m-%d"),
            "$lte": timezone.datetime.strptime(get_params['end_date'], "%Y-%m-%d") + timedelta(days=1)
        }

    return filters

@registered_user_only
@organization_console()
def api_graph_data(request, org, graph_uid):
    """
    Custom API to return graph data.

    **TYPE**: GET

    TODO:
        - Make this API private for single user as well as for organization.

    **Authors**: Gagandeep Singh
    """

    try:
        filters = {
            "graph_uid": graph_uid
        }
        if org:
            filters['organization_id'] = org.id

        try:
            data_filters = parse_graph_filters(request.GET)
        except KeyError:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='Some parameters missing.').gen_http_response()

        graph_diag = GraphDiagram.objects.get(**filters)

        data = graph_diag.get_data(data_filters=data_filters, use_string='true')

        return ApiResponse(status=ApiResponse.ST_SUCCESS, message='ok', data=data).gen_http_response()
    except GraphDiagram.DoesNotExist:
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Invalid graph reference.').gen_http_response()



