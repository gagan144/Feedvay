# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.paginator import Paginator
from tastypie.exceptions import Unauthorized

from accounts.models import RegisteredUser
from accounts.utils import has_necessary_permissions

class GenericTastypieObject(object):
    """
    Generic object to shove data in/get data for tastypie resources.

    Link: http://django-tastypie.readthedocs.io/en/latest/non_orm_data_sources.html

    **Authors**: Gagandeep Singh
    """
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data

class StaffSessionAuthentication(SessionAuthentication):
    """
    Django tastypie session authentication for resources to allow access only to staff user.
    This class extends :class:`tastypie.authentication.SessionAuthentication`. It first authenticates
    user session and then checks staff privilages.

    **Authors**: Gagandeep Singh
    """
    def is_authenticated(self, request, **kwargs):
        """
        Authenticates staff user session.
        :return: Returns True if user is staff else False
        """
        session_ok = super(StaffSessionAuthentication, self).is_authenticated(request, **kwargs)

        if session_ok and (request.user.is_staff or request.user.is_superuser):
            return True
        else:
            return False

class OrgConsoleSessionAuthentication(SessionAuthentication):
    """
    Django tastypie session authentication for resources used in organization console.
    This class extends :class:`tastypie.authentication.SessionAuthentication`. It first authenticates
    user session and then check presence of ``curr_org`` in ``request`` as created by
    :class:`console.middleware.OrgConsoleMiddleware` middleware. If the variable is found,
    access is authenticated otherwise authentication fails.

    Moreover, it also verifies if user has certain permissions to access the resource. If not,
    authentication fails. It permitted, it set ``permissions`` in ``request``.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, required_permissions, all_required=True, allow_bypass=False):
        if not isinstance(required_permissions, list):
            raise Exception("required_permissions must be a list.")

        self.required_permissions = required_permissions
        self.all_required = all_required
        self.allow_bypass = allow_bypass

    def is_authenticated(self, request, **kwargs):
        """
        Authenticates user session and brand.
        :return: Returns True if everything this is ok else False.
        """
        session_ok = super(OrgConsoleSessionAuthentication, self).is_authenticated(request, **kwargs)
        if session_ok:
            try:
                reg_user = request.user.registereduser      # Already taken care by the middleware only if ``c`` param is present
                org = request.curr_org

                perm_json = reg_user.get_all_permissions(org)

                is_permitted = has_necessary_permissions(
                    perm_json = perm_json,
                    required_perms = self.required_permissions,
                    all_required = self.all_required
                )

                if is_permitted is False:
                    return False

                # Set permissions in request
                request.permissions = perm_json

                return True

            except RegisteredUser.DoesNotExist:
                # This happens when accessed without context of org and user is not RegisterUser.
                return False
            except AttributeError:
                # AttributeError: 'curr_org' was not in request
                if self.allow_bypass:
                    # Context: Logged-in user
                    return True
                else:
                    # Context: Organization
                    return False
        else:
            return False


class NoPaginator(Paginator):
    """
    Django tastypie paginator to completely disable pagination. Use this paginator in the
    resource meta option ``paginator_class``.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, request_data, objects, resource_uri=None, limit=None, offset=0, max_limit=1000, collection_name='objects'):
        self.request_data = request_data
        self.objects = objects
        self.resource_uri = resource_uri
        self.collection_name = collection_name

    def page(self):
        count = self.get_count()
        objects = self.objects

        meta = {
            'total_count': count,
        }

        return {
            self.collection_name: objects,
            'meta': meta,
        }

class SurveySessionAuthentication(SessionAuthentication):
    """
    Django tastypie session authentication to allow access to permissible survey resources.

    TODO: Implementation pending

    **Authors**: Gagandeep Singh
    """
    pass