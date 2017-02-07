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
    View for user's management console page.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    reg_user = request.user.registereduser

    data = {
        "app_name": "app_home",
        "Organization": Organization,
        "list_organizations": Organization.objects.filter(organizationmember__registered_user=reg_user, organizationmember__deleted=False)
    }
    return render(request, 'console/home.html', data)
