# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http.response import Http404
from django.db.models import Q

from clients.models import Organization, OrganizationMember
from utilities.decorators import registered_user_only

@registered_user_only
def  home(request):
    """
    View for user management console page.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    reg_user = request.user.registereduser

    # Check if it is organization home
    if request.GET.get('c', None):
        # Organization console
        org_uid=request.GET['c']

        try:
            # Get organization to which this user is a member
            org = Organization.objects.get(
                Q(organizationmember__organization__org_uid = org_uid, organizationmember__registered_user = reg_user) &
                ~Q(status=Organization.ST_DELETED)
            )

            request.curr_org = org

            data = {
                "app_name": "app_home_org"
            }
            return render(request, 'clients/console/home_org.html', data)
        except (ValueError, Organization.DoesNotExist):
            # ValueError: If c is badly formed hexadecimal UUID string, DoesNotExist: Org not found
            raise Http404("Invalid link.")
    else:
        # User console
        data = {
            "app_name": "app_home",
            "Organization": Organization,
            "list_organizations": Organization.objects.filter(organizationmember__registered_user=reg_user, organizationmember__deleted=False)
        }
        return render(request, 'console/home.html', data)
