# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.http.response import Http404
from django.core.urlresolvers import reverse
from accounts.models import RegisteredUser
from brands.models import Brand, BrandOwner


class ConsoleBrandSwitchMiddleware(MiddlewareMixin):
    """
    Middleware to handle user console url or user brand url. User console urls and user
    brand urls are same except the fact that all brand console url are prefixed with
    ``/b/<brand_uid>``. For example:

        - **User console urls**: /console/path/to/app/page/
        - **User brand urls**:   /console/b/<brand_uid>/path/to/app/page/


    This middleware first checks url against regex ``/console/b/<brand_uid>/``, if there is a match then

        - It retrieves brand using 'brand_uid' from database.
        - Create a variable variable ``curr_brand`` inside request.
        - Strips off ``/b/<brand_uid>/`` from url and set ``request.path_info`` to new url against which view has been defined.
        - Corresponding view is then called as per the normal url.

    If url is not matched with regex, then all checks are simply bypassed.

    In this way, even if url has brand information in prefix, same view is used for user's console as well as user's brand console.

    **Authors**: Gagandeep Singh
    """

    def process_request(self, request):
        curr_url = request.path

        # Only consider '/console/b/.....' url, bypass otherwise
        if curr_url.startswith('/console/b/'):
            # Check if user is logged in
            if request.user.is_authenticated():
                split_url = curr_url.split('/')

                if split_url[2] == 'b':
                    # Get brand_uid from url
                    brand_uid = split_url[3]
                    try:
                        # Check if user is registered user
                        reg_user = request.user.registereduser

                        # Fetch brand from db
                        brand = Brand.objects.get(brand_uid=brand_uid)

                        # Check if any user association with brand; permission aloowed or not
                        try:
                            # (1) Brand ownership
                            ownership = BrandOwner.objects.get(brand_id=brand.id, registered_user_id=reg_user.id)

                            # Set brand in request object so that it can be used in templates
                            request.curr_brand = brand
                        except BrandOwner.DoesNotExist:
                            # Ownership not found
                            # (2) Check any other association or brand access
                            pass

                            return HttpResponseForbidden('You do not have permissions to access this page.')

                        # Everything ok here now; prepare for routing
                        # Create new path by stripping off '/b/<brand_uid>/' from curr_url
                        split_url.__delitem__(3)
                        split_url.__delitem__(2)

                        new_path = '/'.join(split_url)

                        # DANGER: using 'request.path = new_path' creates endless looping
                        # Override request path so that view can be resolved
                        request.path_info = new_path
                    except RegisteredUser.DoesNotExist:
                        # User is not a registered user
                        return HttpResponseForbidden('You do not have permissions to access this page.')
                    except ValueError:
                        # Invalid uuid for brand_uid, throws 'ValueError: badly formed hexadecimal UUID string'
                        raise Http404("Invalid brand link.")
                    except Brand.DoesNotExist:
                        # Brand was not found
                        raise Http404("Invalid brand link.")
            else:
                # /if request.user.is_authenticated():
                # Not authenticated; redirect to login
                # Since login url does not begins with '/console/b/', this middleware will bypass check
                return HttpResponseRedirect(reverse('accounts_login') + '?next=' + curr_url)
