# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

class InvalidRegisteredUser(Exception):
    """
    Exception to be used when an Invalid 'RegisteredUser' is encountered.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message='Invalid registered user.'):
        super(InvalidRegisteredUser, self).__init__(message)