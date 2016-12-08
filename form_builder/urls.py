# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.conf.urls import url, include

from form_builder import views
from form_builder import api

# api_forms = api.FormsAPI()

partial_patterns = [
    url(r'^form-field/(?P<class_name>.*).html', views.partials_form_field, name='form_builder_partials_formfield'),
    url(r'^form-layout/(?P<class_name>.*).html', views.partials_form_layout, name='form_builder_partials_formlayout'),
    url(r'^form-condition/(?P<class_name>.*).html', views.partials_form_condition, name='form_builder_partials_formcondition'),
]

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^open/(?P<id>[0-9]+)/$', views.open_form, name='form_builder_open_form'),
    url(r'^update_test/$', views.update_test, name='update_test'),

    url(r'^partials/', include(partial_patterns)),

    # Delete
    url(r'^testing/$', views.testing, name='testing'),

    # Api
    # url(r'^api/', include(api_forms.urls)),
]