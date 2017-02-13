# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include
from console import views

from accounts import views as views_accounts
from clients import views as views_clients
from market import views as views_market

from brands import views as views_brands_xxx
from market import api as api_market
from surveys import views as views_surveys
from surveys import api as api_surveys

url_account = [
    url(r'^settings/$', views_accounts.console_account_settings, name='console_accounts_settings'),
    url(r'^settings/basic-info/update/$', views_accounts.console_account_settings_basicinfo_update, name='console_account_settings_basicinfo_update'),
    url(r'^settings/private-info/update/$', views_accounts.console_account_settings_privinfo_update, name='console_account_settings_privinfo_update'),
    url(r'^settings/email/change/$', views_accounts.console_account_settings_email_change, name='console_account_settings_email_change'),
    url(r'^password/change/$', views_accounts.console_password_change, name='console_password_change'),
]

url_org =[
    url(r'^$', views_clients.console_org_home, name='console_org_home'),
    url(r'^settings/$', views_clients.console_org_settings, name='console_org_settings'),
    url(r'^submit-changes/$', views_clients.console_org_submit_changes, name='console_org_submit_changes'),
]

url_brands = [
    url(r'^$', views_market.console_brands, name='console_market_brands'),
    url(r'^new/$', views_market.console_brand_new, name='console_market_brand_new'),
    url(r'^create/$', views_market.console_brand_create, name='console_market_brand_create'),
    url(r'^edit/$', views_market.console_brand_edit, name='console_market_brand_edit'),
    url(r'^save-changes/$', views_market.console_brand_save_changes, name='console_market_brand_save_changes'),
]


url_brands_xxx = [
    url(r'^$', views_brands_xxx.console_brands, name='console_brands'),
    url(r'^new/$', views_brands_xxx.console_brand_new, name='console_brand_new'),
    url(r'^create/$', views_brands_xxx.console_brand_create, name='console_brand_create'),
    url(r'^request-update/$', views_brands_xxx.console_brand_request_update, name='console_brand_request_update'),  # Only for brand console

    url(r'^disassociate/$', views_brands_xxx.console_brand_disassociate, name='console_brand_disassociate'),    # Only for brand console
    url(r'^toggle-active/$', views_brands_xxx.console_toggle_brand_active, name='console_toggle_brand_active'),    # Only for brand console

    # Api
    # url(r'^api/', include(api_brand_change_req.urls)),
]

api_survey_responses = api_surveys.SurveyResponsesAPI()
api_survey_response_trend = api_surveys.SurveyResponseTrendAPI()
url_surveys = [
    url(r'^$', views_surveys.console_surveys, name='console_surveys'),
    url(r'^new/$', views_surveys.console_survey_new, name='console_survey_new'),
    url(r'^create/$', views_surveys.console_survey_create, name='console_survey_create'),

    url(r'^(?P<survey_uid>\w+)/$', views_surveys.console_survey_panel, name='console_survey_panel'),
    url(r'^(?P<survey_uid>\w+)/save/$', views_surveys.console_survey_save, name='console_survey_save'),
    url(r'^(?P<survey_uid>\w+)/transit/$', views_surveys.console_survey_transit, name='console_survey_transit'),

    url(r'^(?P<survey_uid>\w+)/edit/$', views_surveys.console_survey_phase_form_editor, name='console_survey_simple_form_editor'),
    url(r'^(?P<survey_uid>\w+)/edit/(?P<phase_id>[0-9]+)/$', views_surveys.console_survey_phase_form_editor, name='console_survey_phase_form_editor'),
    url(r'^(?P<survey_uid>\w+)/(?P<phase_id>[0-9]+)/save/$', views_surveys.console_survey_phase_form_save, name='console_survey_phase_form_save'),

    url(r'^(?P<survey_uid>\w+)/response/(?P<response_uid>.*)/$', views_surveys.console_survey_response, name='console_survey_response'),
    url(r'^response/suspicion/remove/$', views_surveys.console_remove_response_suspicion, name='console_survey_remove_response_suspicion'),
    url(r'^response/suspicion/add/$', views_surveys.console_add_response_suspicion, name='console_survey_add_response_suspicion'),

    # Api
    url(r'^api/', include(api_survey_responses.urls)),
    url(r'^api/', include(api_survey_response_trend.urls)),
]

urlpatterns = [
    url(r'^$', views.home, name='console_home'),

    url(r'^account/', include(url_account)),
    url(r'^settings/$', views_brands_xxx.console_brand_settings, name='console_brand_settings'),    # Only for brand console

    url(r'^org/', include(url_org)),
    url(r'^brands/', include(url_brands)),
    url(r'^brands_xxx/', include(url_brands_xxx)),
    url(r'^surveys/', include(url_surveys)),
]