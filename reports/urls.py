# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from reports import views

urlpatterns = [

    # Custom API
    url(r'^api/graph_data/(?P<graph_uid>.*)/$', views.api_graph_data, name='reports_api_graph_data'),
]