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

# ----- Delete -----
def testing(request):
    from form_builder.utils import JsCompilerTool
    comp = JsCompilerTool("$scope.constants.const_int_2 + $scope.data.fld_num_2 + $scope.data.fld_decimal_2_1");
    result = comp.extract_variables()
    return HttpResponse("Done! Use debug mode.")
# ----- /Delete -----

def update_test(request):
    from test_schema import upsert_test_schema
    from django.http import HttpResponse

    form = upsert_test_schema()
    return HttpResponse("Form '{}' updated to version '{}'.".format(form.id, form.version))

def open_form(request, id):
    form = Form.objects.get(id=id)
    template = 'themes/{}/form_base.html'.format(form.theme_skin.theme.code)
    data = {
        'title': form.title,
        'theme': form.theme_skin.theme,
        'skin': form.theme_skin,
        'form': form,
        'lookup_translations': form.get_translation_lookup(),
        'DEFAULT_LANGUAGE_CODE': Language.DEFAULT_LANGUAGE_CODE,    # Fallback language incase translation not found
        'USER_DEFAULT_LANG_CODE': 'hin' #Language.DEFAULT_LANGUAGE_CODE  # Use preferred language
    }
    return render(request, template, data)

# ----- Form Designer -----
@login_required
def form_designer(request, id=None):
    data = {
        'list_languages': Language.objects.filter(active=True),
        'GeoLocation': GeoLocation
    }

    if id:
        form = Form.objects.get(id=id)
        data['form'] = form
    return render(request, 'form_builder/form_designer.html', data)
# ----- /Form Designer -----


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

