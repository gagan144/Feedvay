# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http.response import Http404

from clients.models import Organization, OrganizationMember
from utilities.decorators import registered_user_only

@registered_user_only
def  home(request):
    """
    View for user management console page.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    # Check if it is organization home
    if request.GET.get('c', None):
        # Organization console
        try:
            org = Organization.objects.get(org_uid=request.GET['c'])
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
        reg_user = request.user.registereduser
        data = {
            "app_name": "app_home",
            "Organization": Organization,
            "list_organizations": Organization.objects.filter(organizationmember__registered_user=reg_user, organizationmember__deleted=False)
        }
        return render(request, 'console/home.html', data)
