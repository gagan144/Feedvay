# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import ujson

class ApiResponse(object):
    """
    A class to create a http json response mostly used to cater API requests.

    The content of the response is as follows:

        >>> { "code": <int http code>, "status": "<status>", "message":"<message">, ... }

    .. note::
        Response created by this class is always http 200 OK.

    **Authors**: Gagandeep Singh
    """

    # --- enums ---
    ST_SUCCESS = 'success'
    ST_PARTIAL_SUCCESS = 'partial_success'
    ST_IGNORED = 'ignored'        # No update or change
    ST_FAILED = 'failed'          # Operation failed
    ST_NOT_ALLOWED = 'not_allowed'    # GET or POST not allowed
    ST_FORBIDDEN = 'forbidden'        # Access is not allowed or prohibited
    ST_UNAUTHORIZED = 'unauthorized ' # Authentication fails
    ST_BAD_REQUEST = 'bad_request'    # Bad request formation/Invalid or missing parameteres
    ST_SERVER_ERROR = 'server_error'  # Any internal server error

    CH_STATUS = (
        (ST_SUCCESS, 'Success'),
        (ST_PARTIAL_SUCCESS, 'Partial success'),
        (ST_IGNORED, 'Ignored'),
        (ST_FAILED , 'Failed'),
        (ST_NOT_ALLOWED, 'Not Allowed'),
        (ST_FORBIDDEN, 'Forbidden'),
        (ST_UNAUTHORIZED, 'Unauthorized'),
        (ST_BAD_REQUEST, 'Bad request'),
        (ST_SERVER_ERROR, 'Server error'),
    )

    STATUS_CODES = {
        ST_SUCCESS: 200,
        ST_PARTIAL_SUCCESS: 206,
        ST_IGNORED: 204,
        ST_FAILED: 299,
        ST_NOT_ALLOWED: 405,
        ST_FORBIDDEN: 403,
        ST_UNAUTHORIZED: 401,
        ST_BAD_REQUEST: 400,
        ST_SERVER_ERROR: 500
    }

    # --- Fields ---
    __data = {}

    @property
    def code(self):
        return self.__data['code']

    @property
    def status(self):
        return self.__data['status']

    @property
    def data(self):
        return self.__data

    def __init__(self, status, message, **kwargs):
        data = {

            "status": status,
            "message": message
        }

        data.update(**kwargs)

        # Validate
        self.__validate(data)

        data["code"] = ApiResponse.STATUS_CODES[status]
        self.__data = data

    def __validate(self, data):
        status = data['status']
        is_valid = False
        for k,v in ApiResponse.CH_STATUS:
            if k == status:
                is_valid = True
                break

        if not is_valid:
            raise ValidationError("Invalid status '{}'.".format(status))

    # --- Methods ---
    def set(self, key, value):
        """
        Method to add or update a key-value pair to response json data.
        """
        if key in ['code', 'status']:
            raise Exception("Key should be one of 'code', 'status'")

        self.__data[key] = value

    def change_status(self, status):
        """
        Method to change status.
        """
        data = self.__data.copy()
        data['status'] = status

        # Validate
        self.__validate(data)

        self.__data['status'] = status
        self.__data['code'] = ApiResponse.STATUS_CODES[status]


    def gen_http_response(self):
        """
        Method to generate http response instance. Return this from the view.

        :return: Returns :class:`django.http.JsonResponse` instance
        """

        return JsonResponse(self.__data)