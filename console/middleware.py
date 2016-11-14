# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.utils.deprecation import MiddlewareMixin
from django.http.response import Http404

from brands.models import Brand


class ConsoleBrandSwitchMiddleware(MiddlewareMixin):
    """
    Middleware to handle user console url or user brand url. User console urls and user
    brand urls are same except the fact that all brand console url are prefixed with
    ``/b/<brand_uid>``. For example:
        - **User console urls**: /console/path/to/app/page/
        - **User brand urls**:   /console**/b/<brand_uid>**/path/to/app/page/


    This middleware first checks url against regex ``/console/b/<brand_uid/``, if there is a match then

        - It retrieves brand using 'brand_uid' from database.
        - Create a variable variable ``curr_brand`` inside request.
        - Strips off '/b/<brand_uid>/' from url and set ``request.path_info`` to new url against which view has been defined.
        - Corresponding view is then called as per the normal url.

    If url is not matched with regex, then middleware is simply bypassed.

    In this way, even if url has brand information in prefix, same view is used for user's console as well as user's brand console.

    **Authors**: Gagandeep Singh
    """
    def process_request(self, request):
        curr_url = request.path
        if curr_url.startswith('/console/b/'):
            split_url = curr_url.split('/')

            if split_url[2] == 'b':
                # Get current brand
                brand_uid = split_url[3]
                try:
                    request.curr_brand = Brand.objects.get(brand_uid=brand_uid)

                    # Create new path by stripping off /b/<brand_uin>/ from curr_url
                    split_url.__delitem__(3)
                    split_url.__delitem__(2)

                    new_path = '/'.join(split_url)

                    # request.path = new_path   # DANGER: Using this creates endless looping
                    request.path_info = new_path
                except ValueError:
                    # ValueError: badly formed hexadecimal UUID string
                    raise Http404("Invalid brand link.")
                except Brand.DoesNotExist:
                    raise Http404("Invalid brand link.")

