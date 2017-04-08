# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

class InvalidGraphDefinition(Exception):
    """
    Exception for invalid graph definition.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidGraphDefinition, self).__init__(message)