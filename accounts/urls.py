# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url

from accounts import views

urlpatterns = [
    # Login
    url(r'^login/$', views.login, name="accounts_login"),
    url(r'^logout/$', views.logout, name="accounts_logout"),

    # Registration
    url(r'^signup/$', views.registration, name='accounts_registration'),
    url(r'^registration/verify/$', views.registration_verify, name='accounts_registration_verify'),
    url(r'^registration/closed/$', views.registration_closed, name='accounts_registration_closed'),
    url(r'^registration/resend-code/$', views.registration_resend_code, name='accounts_registration_resend_code'),

    # Password recovery
    url(r'^recovery/plea/$', views.reset_password_plea, name='accounts_reset_password_plea'),
    url(r'^recovery/plea/verify/$', views.reset_password_plea_verify, name='accounts_reset_password_plea_verify'),
    url(r'^recover-account/$', views.recover_account, name='accounts_recover_account'),
]