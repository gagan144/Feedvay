# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url,Http404
from django.db.models import Q

from accounts.models import RegisteredUser
from clients.models import Organization

class OrgConsoleMiddleware(MiddlewareMixin):
    """
    Middleware to handle organization related console pages. All url request which has
    parameter ``c`` in GET or POST are considered to be in context of an organization with
    ``org_uid`` as ``c``.

    **The basic purpose of this middleware is to add ``curr_org`` in ``request``.**

    **Flow**:

        - The middleware first looks for ``c`` in GET and then in POST.
        - If not found, request is bypassed.
        - If found, it identifies the :class:`account.models.RegisteredUser`. Returns HttpResponseForbidden if not found.
        - It then fetches the :class:`clients.models.Organization` having the user as its member.
        - If organization found, it populates ``request.curr_org`` with the organization.
        - If not found, returns HttpResponseForbidden


    **Failure outputs** (only incase ``c`` is found):

        - HttpResponseForbidden:
            - If user is not valid registered user
            - Organization not found
            - User is not a member of the organization

        - Http404:
            - ``c`` is not well form uuid

    .. warning::
        This middleware does not check user permissions. These must be checked after separately.

    **Authors**: Gagandeep Singh
    """
    def process_request(self, request):
        # Check only if logged-in otherwise skip
        if request.user.is_authenticated():
            # Look for 'c' paramtere in GET or POST
            if request.GET.get('c', None):
                org_uid = request.GET['c']
            elif request.POST.get('c', None):
                org_uid = request.POST['c']
            else:
                org_uid = None

            if org_uid:
                # Request is in context to an organization
                try:
                    reg_user = request.user.registereduser

                    # (a) Get organization to which this user is a member
                    org = Organization.objects.get(
                        Q(organizationmember__organization__org_uid=org_uid, organizationmember__registered_user=reg_user, organizationmember__deleted=False) &
                        ~Q(status=Organization.ST_DELETED)
                    )
                    request.curr_org = org

                except (RegisteredUser.DoesNotExist, Organization.DoesNotExist):
                    return HttpResponseForbidden('You do not have permissions to access this page.')
                except ValueError:
                    # ValueError: If c is badly formed hexadecimal UUID string
                    raise Http404("Invalid link.")

