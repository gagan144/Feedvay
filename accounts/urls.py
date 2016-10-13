# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url

from accounts import views

urlpatterns = [
    # Registration
    url(r'^signup/$', views.registration, name='accounts_registration'),
    url(r'^registration/verify/$', views.registration_verify, name='accounts_registration_verify'),
    url(r'^registration/closed/$', views.registration_closed, name='accounts_registration_closed'),
]