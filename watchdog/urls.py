# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf.urls import url

from watchdog import views

urlpatterns = [
    # ReportedProblems
    url(r'^report-problem/new/$', views.report_problem_new, name="watchdog_report_problem_new"),

    # Suggestions
    url(r'^suggestion/new/$', views.suggestion_new, name="watchdog_suggestion_new"),
]