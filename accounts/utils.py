# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.contrib.auth.models import User
import os, json

from django.contrib.auth.models import Permission

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

# ----- Permissions utils -----
def lookup_permission(perm_json, perm_key):
    """
    Method to lookup for a permission in permission json. A permission lookup can be based on app model or app model CRUDs.

    :param perm_json: Permission JSON
    :param perm_key: ``.`` separated permission key of format ``<app-label>.<model-name>`` or ``<app-label>.<model-name>.<perm-codename>``
    :return: True if json has permission else false

    **Authors**: Gagandeep Singh
    """

    key_split = perm_key.split('.')

    # Validate
    key_len = len(key_split)
    if key_len not in [2,3]:
        raise ValueError("Invalid perm_key '{}'. Allowed format: '<app-label>.<model-name>' or '<app-label>.<model-name>.<perm-codename>'.".format(perm_key))

    app_n_model = ".".join(key_split[:2])
    app_n_model_json = perm_json.get(app_n_model, None)

    if app_n_model_json:
        if key_len == 2:
            # App model lookup
            return True
        else:
            # App model CRUD lookup
            return True if app_n_model_json.get('permissions', []).__contains__(key_split[2]) else False
    else:
        return False


def has_necessary_permissions(perm_json, required_perms, all_required=True):
    """
    Method to check if given permission json has all necessary permissions. The necessity has
    be all permissions are strictly required (AND operation) or atleast one perission is required
    (OR operation).

    :param perm_json: Permission JSON
    :param required_perms: String or list of permission key of format ``<app-label>.<model-name>.<perm-codename>``.
    :param all_required: If True, all permissions are required else atleast one.
    :return: True if necessity is met else False

    **Authors**: Gagandeep Singh
    """

    # Make list if not required_perms is string
    if isinstance(required_perms, str) or isinstance(required_perms, unicode):
        list_perms = [required_perms]
    else:
        list_perms = required_perms

    # Loop and check presence
    is_permitted = True
    for perm_key in list_perms:
        is_present = lookup_permission(perm_json, perm_key)

        if all_required:
            # All required: AND operation
            is_permitted = is_permitted and is_present
            if not is_permitted:
                break
        else:
            # Atleast one required: OR operation
            is_permitted = is_permitted or is_present


    return is_permitted

def get_superuser_perm_json():
    """
    Method to read return superuser permissions json from ``accounts/data/superuser.json`` files.

    :return: Dict

    **Authors**: Gagandeep Singh
    """

    file_path = os.path.join(os.path.dirname(__file__), 'data/superuser.json')
    with open(file_path, 'r') as f:
        perm_json = json.load(f)

    return perm_json

def get_all_superuser_permission_codenames():
    """
    Method to return all permission codenames for superuser access.
    This method reads ``accounts/data/superuser.json`` file, iterates over all keys
    and returns list of permissions codenames.

    :return: List

    **Authors**: Gagandeep Singh
    """

    file_path  = os.path.join(os.path.dirname(__file__), 'data/superuser.json')
    with open(file_path, 'r') as f:
        perm_json = json.load(f)

    list_perms = []
    for key in perm_json:
        list_perms += perm_json[key]['permissions']

    return list_perms

def get_all_superuser_permissions():
    """
    Method to return all :class:`django.contrib.auth.models.Permission` for superuser access.
    This method uses :py:func:`accounts.utils.get_all_superuser_permission_codenames` to obtain all
    superuser permission codenames.

    :return: List<:class:`django.contrib.auth.model.Permission`>

    **Authors**: Gagandeep Singh
    """
    list_codenames = get_all_superuser_permission_codenames()
    return Permission.objects.filter(codename__in=list_codenames).select_related('content_type').order_by('content_type__model', 'codename')

# ----- /Permissions utils -----