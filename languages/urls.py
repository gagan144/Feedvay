# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url, include

from languages import views
from languages import api

# api_translations = api.TranslationsAPI()
api_translation_search = api.TranslationSearchAPI()

urlpatterns = [
    url(r'^form/(?P<form_id>[0-9]+)/translations.js$', views.form_translations, name='languages_form_translations'),

    # # Staff admin
    # url(r'^translations/save/$', views.save_translation, name='languages_translations_save'),

    # Api
    # url(r'^api/', include(api_translations.urls)),  # Staff admin
    url(r'^api/', include(api_translation_search.urls)),
]