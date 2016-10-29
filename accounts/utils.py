# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib.auth.models import User
from accounts.models import RegisteredUser

class ClassifyRegisteredUser:
    """
    Utility class to classify user given its username. This is useful in situations
    such as registration where entered username must be checked for availability, validity,
    incomplete registration state etc.

    Following table describes the classification of the user on basis of certain parameters:

    +--------------+------------------------+-------------+-----------------------------------+
    | User model   | RegisteredUser model   | Class       | Remarks                           |
    +==============+========================+=============+===================================+
    | Not present  |                        | NEW         | New user, allow registration.     |
    +--------------+------------------------+-------------+-----------------------------------+
    | Present(any) |                        | STAFF       | Staff user, deny registration.    |
    +--------------+------------------------+-------------+-----------------------------------+
    | Inactive     | Status: lead           | UNVERIFIED  | Override user with new details.   |
    +--------------+------------------------+-------------+-----------------------------------+
    | Inactive/Ac  | Status: verif. pending | UNVERIFIED  | Override user with new details.   |
    +--------------+------------------------+-------------+-----------------------------------+
    | Inactive     | Status: verified       | SUSPENDED   | User account suspended. Deny.     |
    +--------------+------------------------+-------------+-----------------------------------+
    | Active       | Status: verified       | VERIFIED    | Already registered user.          |
    +--------------+------------------------+-------------+-----------------------------------+


    **Authors**: Gagandeep Singh
    """

    NEW = 'new'
    STAFF = 'staff'
    UNVERIFIED = 'unverified'
    VERIFIED = 'verified'
    SUSPENDED = 'suspended'

    @staticmethod
    def classify(username):
        try:
            user = User.objects.get(username=username)

            try:
                reg_user = user.registereduser
                status = reg_user.status

                if user.is_active:
                    if status == RegisteredUser.ST_VERIFICATION_PENDING:
                        return ClassifyRegisteredUser.UNVERIFIED
                    elif status == RegisteredUser.ST_VERIFIED:
                        return ClassifyRegisteredUser.VERIFIED
                    else:
                        raise Exception("Unhandled case with user:active and reg_user.status:{}".format(status))
                else:
                    if status in [RegisteredUser.ST_LEAD, RegisteredUser.ST_VERIFICATION_PENDING]:
                        return ClassifyRegisteredUser.UNVERIFIED
                    elif status == RegisteredUser.ST_VERIFIED:
                        return ClassifyRegisteredUser.SUSPENDED
                    else:
                        raise Exception("Unhandled case with user:active and reg_user.status:{}".format(status))

            except RegisteredUser.DoesNotExist:
                return ClassifyRegisteredUser.STAFF

        except User.DoesNotExist:
            return ClassifyRegisteredUser.NEW
