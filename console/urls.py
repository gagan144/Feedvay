# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include
from console import views

from accounts import views as views_accounts
from clients import views as views_clients
from market import views as views_market
from feedback import views as views_feedback

from accounts import api as api_accounts
from clients import api as api_clients
from market import api as api_market
from surveys import views as views_surveys
from surveys import api as api_surveys
from storeroom import api as api_storeroom
from feedback import api as api_feedback

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


api_organization_roles = api_accounts.OrganizationRolesAPI()
api_organization_members = api_clients.OrganizationMembersAPI()
url_team = [
    url(r'^$', views_clients.console_team, name='console_team'),

    url(r'^roles/new/$', views_clients.console_organization_role_new, name='console_team_organization_role_new'),
    url(r'^roles/create/$', views_clients.console_organization_role_create, name='console_team_organization_role_create'),
    url(r'^roles/edit/(?P<org_role_id>[0-9]+)/$', views_clients.console_organization_role_edit, name='console_team_organization_role_edit'),
    url(r'^roles/edit-save/(?P<org_role_id>[0-9]+)/$', views_clients.console_organization_role_edit_save, name='console_team_organization_role_edit_save'),

    url(r'^member/new/$', views_clients.console_member_new, name='console_team_member_new'),
    url(r'^member/invite/$', views_clients.console_member_invite, name='console_team_member_invite'),
    url(r'^member/edit/(?P<org_mem_id>[0-9]+)/$', views_clients.console_member_edit, name='console_team_member_edit'),
    url(r'^member/edit-save/(?P<org_mem_id>[0-9]+)/$', views_clients.console_member_edit_save, name='console_team_member_edit_save'),
    url(r'^member/remove/(?P<org_mem_id>[0-9]+)/$', views_clients.console_member_remove, name='console_team_member_remove'),

    # Api
    url(r'^api/', include(api_organization_roles.urls)),
    url(r'^api/', include(api_organization_members.urls)),
]

url_brands = [
    url(r'^$', views_market.console_brands, name='console_market_brands'),
    url(r'^new/$', views_market.console_brand_new, name='console_market_brand_new'),
    url(r'^create/$', views_market.console_brand_create, name='console_market_brand_create'),
    url(r'^edit/$', views_market.console_brand_edit, name='console_market_brand_edit'),
    url(r'^save-changes/$', views_market.console_brand_save_changes, name='console_market_brand_save_changes'),
]

api_org_bsp = api_market.OrgBspAPI()
url_bsp = [
    url(r'^$', views_market.console_bsp_panel, name='console_market_bsp_panel'),
    url(r'^customize-type/new/$', views_market.console_bsp_customize_type, name='console_market_customize_type'),
    url(r'^customize-type/create/$', views_market.console_bsp_customize_type_create, name='console_market_customize_type_create'),
    url(r'^customize-type/edit/(?P<cust_id>[0-9]+)/$', views_market.console_bsp_customize_type_edit, name='console_market_customize_type_edit'),
    url(r'^customize-type/edit-save/(?P<cust_id>[0-9]+)/$', views_market.console_bsp_customize_type_edit_save, name='console_market_customize_type_edit_save'),
    url(r'^customize-type/remove/(?P<cust_id>[0-9]+)/$', views_market.console_bsp_customize_type_remove, name='console_market_customize_type_remove'),

    url(r'^import/$', views_market.console_bsp_import, name='console_market_bsp_import'),
    url(r'^import/download-excel-format/$', views_market.console_bsp_import_download_excel_format, name='console_market_bsp_import_download_excel_format'),
    url(r'^import/upload-excel/$', views_market.console_bsp_import_upload_excel, name='console_market_bsp_import_upload_excel'),
    url(r'^import/queue/$', views_market.console_bsp_import_queue, name='console_market_bsp_import_queue'),
    url(r'^import/remove/$', views_market.console_bsp_import_remove, name='console_market_bsp_import_remove'),

    url(r'^new/$', views_market.console_bsp_new, name='console_market_bsp_new'),
    url(r'^create/$', views_market.console_bsp_create, name='console_market_bsp_create'),
    url(r'^manage/(?P<bsp_id>.*)/$', views_market.console_bsp_manage, name='console_market_bsp_manage'),
    # url(r'^edit/(?P<bsp_id>.*)/$', views_market.console_bsp_edit, name='console_market_bsp_edit'),
    url(r'^edit-save/(?P<bsp_id>.*)/$', views_market.console_bsp_edit_save, name='console_market_bsp_edit_save'),

    # Partials
    url(r'^partials/bsp-type-attr/(?P<bsp_type>.*)/$', views_market.partial_bsp_type_attributes, name='console_market_bsp_type_attr'),

    # Api
    url(r'^api/', include(api_org_bsp.urls)),
]

api_bsp_feedback_forms = api_feedback.BspFeedbackFormsAPI()
api_bsp_feedback_responses = api_feedback.BspFeedbackResponsesAPI()
url_feedback = [
    url(r'^bsp-feedback/$', views_feedback.console_bsp_feedback_panel, name='console_feedback_bsp_panel'),
    url(r'^bsp-feedback/new/$', views_feedback.console_bsp_feedback_new, name='console_feedback_bsp_new'),
    url(r'^bsp-feedback/create/$', views_feedback.console_bsp_feedback_create, name='console_feedback_bsp_create'),
    url(r'^bsp-feedback/manage/(?P<form_id>[0-9]+)/$', views_feedback.console_bsp_feedback_manage, name='console_feedback_bsp_manage'),
    url(r'^bsp-feedback/edit/(?P<form_id>[0-9]+)/$', views_feedback.console_bsp_feedback_edit, name='console_feedback_bsp_edit'),
    url(r'^bsp-feedback/edit-save/(?P<form_id>[0-9]+)/$', views_feedback.console_bsp_feedback_edit_save, name='console_feedback_bsp_edit_save'),
    url(r'^bsp-feedback/associate-bsp/(?P<form_id>[0-9]+)/$', views_feedback.console_bsp_feedback_associate_bsp, name='console_feedback_bsp_associate_bsp'),
    url(r'^bsp-feedback/deassociate-bsp/(?P<form_id>[0-9]+)/$', views_feedback.console_bsp_feedback_deassociate_bsp, name='console_feedback_bsp_deassociate_bsp'),
    url(r'^bsp-feedback/associate-form/(?P<bsp_id>.*)/$', views_feedback.console_bsp_feedback_associate_form, name='console_feedback_bsp_associate_form'),

    # Api
    url(r'^api/', include(api_bsp_feedback_forms.urls)),
    url(r'^api/', include(api_bsp_feedback_responses.urls)),
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

api_import_records_org = api_storeroom.ImportRecordOrgAPI()
url_storeroom = [
    # Api
    url(r'^api/', include(api_import_records_org.urls)),
]

urlpatterns = [
    url(r'^$', views.home, name='console_home'),

    url(r'^account/', include(url_account)),

    url(r'^org/', include(url_org)),
    url(r'^team/', include(url_team)),
    url(r'^brands/', include(url_brands)),
    url(r'^bsp/', include(url_bsp)),
    url(r'^feedback/', include(url_feedback)),
    url(r'^surveys/', include(url_surveys)),
    url(r'^storeroom/', include(url_storeroom)),
]