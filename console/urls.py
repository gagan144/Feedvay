# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include
from console import views

from accounts import views as views_accounts
from brands import views as views_brands
from brands import api as api_brands

url_account = [
    url(r'^settings/$', views_accounts.console_account_settings, name='console_accounts_settings'),
    url(r'^settings/basic-info/update/$', views_accounts.console_account_settings_basicinfo_update, name='console_account_settings_basicinfo_update'),
    url(r'^settings/private-info/update/$', views_accounts.console_account_settings_privinfo_update, name='console_account_settings_privinfo_update'),
    url(r'^settings/email/change/$', views_accounts.console_account_settings_email_change, name='console_account_settings_email_change'),
    url(r'^password/change/$', views_accounts.console_password_change, name='console_password_change'),
]

api_brand_change_req = api_brands.BrandChangeRequestAPI()
url_brands = [
    url(r'^$', views_brands.console_brands, name='console_brands'),
    url(r'^new/$', views_brands.console_brand_new, name='console_brand_new'),
    url(r'^create/$', views_brands.console_brand_create, name='console_brand_create'),
    url(r'^request-update/$', views_brands.console_brand_request_update, name='console_brand_request_update'),  # Only for brand console

    url(r'^disassociate/$', views_brands.console_brand_disassociate, name='console_brand_disassociate'),    # Only for brand console
    url(r'^toggle-active/$', views_brands.console_toggle_brand_active, name='console_toggle_brand_active'),    # Only for brand console

    # Api
    url(r'^api/', include(api_brand_change_req.urls)),
]

urlpatterns = [
    url(r'^$', views.home, name='console_home'),

    url(r'^account/', include(url_account)),

    url(r'^brands/', include(url_brands)),
    url(r'^settings/$', views_brands.console_brand_settings, name='console_brand_settings'),    # Only for brand console
]