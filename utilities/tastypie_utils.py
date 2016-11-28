# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from tastypie.authentication import SessionAuthentication
from tastypie.paginator import Paginator

class BrandConsoleSessionAuthentication(SessionAuthentication):
    """
    Django tastypie session authentication for resources used in brand console.
    This class extends :class:`tastypie.authentication.SessionAuthentication`. It first authenticates
    user session and then check presence of ``curr_brand`` in ``request`` as created by
    :class:`console.middleware.ConsoleBrandSwitchMiddleware` middleware. If the variable is not found,
    access is authenticated otherwise authentication fails.

    **Authors**: Gagandeep Singh
    """
    def is_authenticated(self, request, **kwargs):
        """
        Authenticates user session and brand.
        :return: Returns True if everything this is ok else False.
        """
        session_ok = super(BrandConsoleSessionAuthentication, self).is_authenticated(request, **kwargs)
        if session_ok:
            try:
                curr_brand = request.curr_brand
                return True
            except AttributeError:
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