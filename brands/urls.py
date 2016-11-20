# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from brands.api import *

api_brand_existence = BrandExistenceAPI()

urlpatterns = [

    # Api
    url(r'^api/', include(api_brand_existence.urls)),
]