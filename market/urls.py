# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from market.api import *

api_brand_existence = BrandExistenceAPI()
api_bsp_labels = BspLabelsAPI()

urlpatterns = [

    # Api
    url(r'^brands/api/', include(api_brand_existence.urls)),
    url(r'^bsp/api/', include(api_bsp_labels.urls)),
]