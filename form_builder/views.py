# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from form_builder.models import *
from form_builder.utils import GeoLocation
from form_builder import fields
from form_builder import layouts
from form_builder import conditions
from form_builder import widgets
from languages.models import Language

# ----- Partials -----
def partials_form_field(request, class_name):
    fieldclass = getattr(fields, class_name)

    data = {
        'fieldclass': fieldclass._properties_by_key,
        'widgets': fieldclass.widget.choices,
        'MCQ_Types': fields.MCQ_Types,
        'ChoiceOrder': fields.ChoiceOrder,
        'OtherOptionType': fields.OtherOptionType
    }
    return render(request, 'form_builder/partials/editor/'+class_name+'.html', data)

def partials_form_layout(request, class_name):
    layoutclass = getattr(layouts, class_name)

    data = {
        'layoutclass': layoutclass._properties_by_key,
    }
    return render(request, 'form_builder/partials/editor/'+class_name+'.html', data)

def partials_form_condition(request, class_name):
    conditionclass = getattr(conditions, class_name)

    data = {
        'conditionclass': conditionclass._properties_by_key,
    }
    return render(request, 'form_builder/partials/editor/'+class_name+'.html', data)
# ----- /Partials -----

