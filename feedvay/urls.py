# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
"""feedvay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^console/', include('console.urls')),
    url(r'^watchdog/', include('watchdog.urls')),
    url(r'^clients/', include('clients.urls')),
    url(r'^market/', include('market.urls')),

    url(r'^languages/', include('languages.urls')),
    url(r'^forms/', include('form_builder.urls')),
    url(r'^surveys/', include('surveys.urls')),
    url(r'^geography/', include('geography.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^reports/', include('reports.urls')),

    # Admin and staff
    url(r'^admin/', admin.site.urls),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),    # Django admindocs
    url(r'^admin/doc/(?P<filename>.*)$', views.docs, name='docs'),  # Sphinx documentation
]
