# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from feedback import views

urlpatterns = [
    url(r'^bsp/(?P<bsp_id>\w+)/$', views.open_bsp_feedback, name='feedback_open_bsp'),
    url(r'^submit-bsp-response/$', views.submit_bsp_feedback_response, name='feedback_submit_bsp_response')
]