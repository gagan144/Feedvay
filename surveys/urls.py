# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from surveys import views

urlpatterns = [
    url(r'^(?P<survey_uid>\w+)(/|/(?P<phase_id>[0-9]+)/)$', views.open_survey_form, name='surveys_open_form'),
    url(r'^submit-response/$', views.submit_survey_response, name='surveys_submit_response'),
]