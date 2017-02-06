# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from clients.api import *

api_org_existence = OrgExistenceAPI()

urlpatterns = [

    # Api
    url(r'^api/', include(api_org_existence.urls)),
]