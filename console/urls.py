# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include
from console import views

from accounts import views as views_accounts
from brands import views as views_brands

url_account = [
    url(r'^settings/$', views_accounts.console_account_settings, name='console_accounts_settings'),
    url(r'^settings/basic-info/update/$', views_accounts.console_account_settings_basicinfo_update, name='console_account_settings_basicinfo_update'),
    url(r'^settings/private-info/update/$', views_accounts.console_account_settings_privinfo_update, name='console_account_settings_privinfo_update'),
    url(r'^password/change/$', views_accounts.console_password_change, name='console_password_change'),
]

url_brands = [
    url(r'^$', views_brands.console_brands, name='console_brands'),
    url(r'^create/$', views_brands.console_create_brand, name='console_brand_create'),
]

urlpatterns = [
    url(r'^$', views.home, name='console_home'),

    url(r'^account/', include(url_account)),
    url(r'^brands/', include(url_brands)),
]