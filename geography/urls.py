# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from geography import views

urlpatterns = [

    # Custom API
    url(r'^api/geolocation-tree/$', views.geolocation_tree, name='geography_geolocation_tree'),
    url(r'^api/search-geolocation/$', views.search_geolocation, name='geography_search_geolocation'),
]