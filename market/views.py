# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render
from django.http.response import Http404
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from openpyxl import Workbook
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from mongoengine.queryset import DoesNotExist as DoesNotExist_mongo
import copy
import json
import re

from accounts.decorators import registered_user_only, organization_console
from market.models import Brand
from market.forms import *
from market import operations as ops
from market.models import *
from market.importers import dump_bsp_bulk_upload
from storeroom.models import ImportRecord
from feedback.models import BspFeedbackForm
from reports.models import GraphDiagram
from utilities.api_utils import ApiResponse

# ==================== Console ====================
# --- Brands ---
@registered_user_only
@organization_console(required_perms='market.brand')
def console_brands(request, org):
    """
    View to display all brands in an organization.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    filter_brands = copy.deepcopy(request.permissions['market.brand']['data_access'])
    if filter_brands is None:
        list_brands = []
    else:
        filter_brands['organization_id'] = org.id
        list_brands = Brand.objects.filter(**filter_brands).only('id', 'name', 'brand_uid', 'logo', 'icon', 'active', 'created_by', 'created_on').select_related('created_by')

    data = {
        'app_name': 'app_brands',
        'list_brands': list_brands
    }

    return render(request, 'market/console/brands.html', data)


@registered_user_only
@organization_console(required_perms='market.brand.add_brand')
def console_brand_new(request, org):
    """
    View to open form to add new brand.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        "app_name": "app_create_brand"
    }
    return render(request, 'market/console/brand_new.html', data)

@registered_user_only
@organization_console(required_perms='market.brand.add_brand')
def console_brand_create(request, org):
    """
    An API view to create a NEW brand. User fills a form and submit data.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form_brand = BrandCreateForm(request.POST, request.FILES)

        if form_brand.is_valid():
            form_data = form_brand.cleaned_data

            ops.create_new_brand(form_data, org, request.user.registereduser)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_brand.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console(required_perms='market.brand.change_brand')
def console_brand_edit(request, org):
    """
    Django view to open brand form.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    try:
        brand_uid = request.GET['brand_uid']

        brand = Brand.objects.get(organization=org, brand_uid=brand_uid)

        data = {
            "app_name": "app_brand_edit",
            "brand": brand
        }

        return render(request, 'market/console/brand_edit.html', data)


    except (KeyError, Brand.DoesNotExist) as ex:
        raise Http404("Invalid link.")

@registered_user_only
@organization_console(required_perms='market.brand.change_brand')
def console_brand_save_changes(request, org):
    """
    An API view to save brand chnages. User fills a form and submit data.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """

    if request.method.lower() == 'post':
        form_brand = BrandEditForm(request.POST, request.FILES)

        if form_brand.is_valid():
            form_brand.save()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_brand.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()
# --- /Brands ---

# --- BusinessServicePoint ---
@registered_user_only
@organization_console()
def console_bsp_panel(request, org):
    """
    Django view to manage organization BSP in terms of type customization, BSP etc.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    data = {
        'app_name': 'app_bsp_panel',
        'list_custom_types': BspTypeCustomization.objects.filter(organization_id=org.id),
        'list_brands': Brand.objects.filter(organization_id=org.id),
        "BspTypes": BspTypes,
        "BusinessServicePoint": BusinessServicePoint,
        "AWS_S3_CUSTOM_DOMAIN": settings.AWS_S3_CUSTOM_DOMAIN
    }

    return render(request, 'market/console/bsp_panel.html', data)

@registered_user_only
@organization_console('market.bsptypecustomization.add_bsptypecustomization')
def console_bsp_customize_type(request, org):
    """
    Django view to customize a BSP type.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    list_available_types = []
    list_used_types = list(BspTypeCustomization.objects.filter(organization_id=org.id).values_list('bsp_type', flat=True))
    for t in BspTypes.choices:
        if t[0] not in list_used_types:
            list_available_types.append({
                "id": t[0],
                "name": t[1]
            })

    list_dtypes = [{"id": dtype[0], "name": dtype[1]} for dtype in BspTypeCustomization.Attribute.ENUMS.CH_DTYPES]
    reserved_labels_common = BusinessServicePoint._fields.keys()
    reserved_labels_common.sort()

    data = {
        'app_name': 'app_customize_bsp_type',
        'list_available_types': list_available_types,
        'list_dtypes': list_dtypes,
        'reserved_labels_common': reserved_labels_common
    }

    return render(request, 'market/console/bsp_customize_type.html', data)

@registered_user_only
@organization_console('market.bsptypecustomization.add_bsptypecustomization')
def console_bsp_customize_type_create(request, org):
    """
    API view to create a bsp type customization.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        data = request.POST.copy()

        form_custm = BspTypeCustomizationForm(data)

        if form_custm.is_valid():
            form_custm.save(organization=org, created_by=request.user)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_custm.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console('market.bsptypecustomization.change_bsptypecustomization')
def console_bsp_customize_type_edit(request, org, cust_id):
    """
    Django view to edit a customized BSP type.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    try:
        filters = copy.deepcopy(request.permissions['market.bsptypecustomization']['data_access'])
        filters['organization_id'] = org.id
        filters['id'] = cust_id

        cust_bsp = BspTypeCustomization.objects.get(**filters)
    except (TypeError, BspTypeCustomization.DoesNotExist):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")


    list_dtypes = [{"id": dtype[0], "name": dtype[1]} for dtype in BspTypeCustomization.Attribute.ENUMS.CH_DTYPES]

    reserved_labels_common = BusinessServicePoint._fields.keys()
    reserved_labels_common.sort()

    type_class = MAPPING_BSP_CLASS[cust_bsp.bsp_type]
    type_wise_labels = type_class.properties().keys()

    data = {
        'app_name': 'app_customize_bsp_type',
        'cust_bsp': cust_bsp,
        'list_dtypes': list_dtypes,
        'reserved_labels_common': reserved_labels_common,
        'type_wise_labels': type_wise_labels
    }

    return render(request, 'market/console/bsp_customize_type_edit.html', data)


@registered_user_only
@organization_console('market.bsptypecustomization.change_bsptypecustomization')
def console_bsp_customize_type_edit_save(request, org, cust_id):
    """
    API view to save edited bsp type customization.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = copy.deepcopy(request.permissions['market.bsptypecustomization']['data_access'])
            filters['organization_id'] = org.id
            filters['id'] = cust_id

            cust_bsp = BspTypeCustomization.objects.get(**filters)
        except (TypeError, BspTypeCustomization.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to edit this customization.").gen_http_response()


        data = request.POST.copy()
        form_custm = BspTypeCustomizationForm(data, instance=cust_bsp)

        if form_custm.is_valid():
            form_custm.save()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_custm.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console('market.bsptypecustomization.delete_bsptypecustomization')
def console_bsp_customize_type_remove(request, org, cust_id):
    """
    API view to delete a bsp type customization.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = copy.deepcopy(request.permissions['market.bsptypecustomization']['data_access'])

            filters['organization_id'] = org.id
            filters['id'] = cust_id

            cust_bsp = BspTypeCustomization.objects.get(**filters)
        except (TypeError, BspTypeCustomization.DoesNotExist):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to remove this customization.").gen_http_response()


        confirm = int(request.POST.get('confirm', 0))

        if not confirm:
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please confirm your action.').gen_http_response()
        else:
            cust_bsp.delete()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_import(request, org):
    """
    Django view to open page for bulk import of bsps.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        'app_name': 'app_bsp_bulk_upload',
        'list_bsp_types': BspTypes.choices,
        'list_brands': Brand.objects.filter(organization=org, active=True).only('id', 'name', 'brand_uid', 'logo')
    }

    return render(request, 'market/console/bsp_bulk_upload.html', data)

@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_import_download_excel_format(request, org):
    """
    Django view to return excel filename for bsp import.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    bsp_type_code = request.GET['type']

    list_attr = get_bsp_labels(bsp_type_code, org)

    workbook = Workbook()
    worksheet = workbook.worksheets[0]

    row_header = [attr['path'] for attr in list_attr]
    row_dtype = [attr['dtype'] for attr in list_attr]

    worksheet.append(row_header)
    worksheet.append(row_dtype)

    # Save & return file
    filename = "{}_bulk_upload_format.xlsx".format(bsp_type_code)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+filename
    workbook.save(response)
    return response


@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_import_upload_excel(request, org):
    """
    API view to process uploaded file for BSP import.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':

        try:
            bsp_type = request.POST['bsp_type']
            file_excel = request.FILES['file_upload']

            count = dump_bsp_bulk_upload(file_excel, bsp_type, org, request.user)

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok. {} bsp queued.'.format(count)).gen_http_response()
        except MultiValueDictKeyError:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='One or more parameters are missing.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()

@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_import_queue(request, org):
    """
    Django view to view all imported BSP in queue and their status.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    data = {
        'app_name': 'app_bsp_bulk_upload_queue',
        'ImportRecord': ImportRecord
    }

    return render(request, 'market/console/bsp_bulk_upload_in_queue.html', data)


@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_import_remove(request, org):
    """
    Django view to remove BSP in imports in queue. Since user with permission
    ``add_businessservicepoint`` can add BSP, this view is protected by same permission,
    meaning if user can can BSP, he can also remove those in queue as well.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            list_ids = request.POST.getlist('list_ids[]')
            if not (isinstance(list_ids, list) and len(list_ids)):
                raise BadValueError("'list_ids' is not a list.")

            with transaction.atomic():
                count = ImportRecord.objects.filter(pk__in=list_ids, status__ne=ImportRecord.ST_PROCESSING).delete()

            partial = True if count != len(list_ids) else False

            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.', count_deleted=count, partial=partial).gen_http_response()
        except (MultiValueDictKeyError, BadValueError):
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message='One or more parameters are missing.').gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_new(request, org):
    """
    Django view to open form for new BSP

    **Type**: GET

    **Authors**: Gagandeep Singh
    """

    list_brands = Brand.objects.filter(organization_id=org.id, active=True)

    data = {
        'app_name': 'app_bsp_edit',

        'list_brands': list_brands,

        'BusinessServicePoint': BusinessServicePoint,
        'BspTypes': BspTypes,
        'ContactEmbDoc': ContactEmbDoc
    }

    return render(request, 'market/console/bsp_new.html', data)


@registered_user_only
@organization_console('market.businessservicepoint.add_businessservicepoint')
def console_bsp_create(request, org):
    """
    API view to create new BSP for submitted form.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        data = json.loads(request.POST.copy()['data'])
        form_bsp = BusinessServicePointForm(data)

        if form_bsp.is_valid():
            form_bsp.save(organization=org, created_by=request.user)
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_bsp.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@registered_user_only
@organization_console('market.businessservicepoint')
def console_bsp_manage(request, org, bsp_id):
    """
    View to manage Business or Service Point.

    **Authors**: Gagandeep Singh
    """
    try:
        filters = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
        filters['organization_id'] = org.id
        filters['pk'] = bsp_id

        bsp = BusinessServicePoint.objects.get(**filters)
    except (TypeError, DoesNotExist_mongo):
        # TypeError: If filters is None
        return HttpResponseForbidden("You do not have permissions to access this page.")

    if bsp.brand_id:
        list_brands = Brand.objects.filter(organization_id=org.id).filter(Q(active=True) | Q(id=int(bsp.brand_id)))
    else:
        list_brands = Brand.objects.filter(organization_id=org.id, active=True)

    data = {
        'app_name': 'app_bsp_edit',

        'bsp': bsp,
        'list_brands': list_brands,
        'list_feedback_forms': BspFeedbackForm.objects.filter(organization_id=org.id).order_by('title').only('id', 'title'),
        'list_graphs_dashboard': GraphDiagram.objects.filter(organization_id=org.id, context=GraphDiagram.CT_BSP_FEEDBACK),

        'BusinessServicePoint': BusinessServicePoint,
        'BspTypes': BspTypes,
        'ContactEmbDoc': ContactEmbDoc
    }

    return render(request, 'market/console/bsp_manage.html', data)


# @registered_user_only
# @organization_console(['market.businessservicepoint.change_businessservicepoint', 'market.businessservicepoint.view_businessservicepoint'])
# def console_bsp_edit(request, org, bsp_id):
#     """
#     Django view to edit organization's BSP.
#
#     **Type**: GET
#
#     **Authors**: Gagandeep Singh
#     """
#
#     try:
#         filters = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
#         filters['organization_id'] = org.id
#         filters['pk'] = bsp_id
#
#         bsp = BusinessServicePoint.objects.get(**filters)
#     except (TypeError, DoesNotExist_mongo):
#         # TypeError: If filters is None
#         return HttpResponseForbidden("You do not have permissions to access this page.")
#
#     if bsp.brand_id:
#         list_brands = Brand.objects.filter(organization_id=org.id).filter(Q(active=True) | Q(id=int(bsp.brand_id)))
#     else:
#         list_brands = Brand.objects.filter(organization_id=org.id, active=True)
#
#     data = {
#         'app_name': 'app_bsp_edit',
#
#         'bsp': bsp,
#         'list_brands': list_brands,
#
#         'BusinessServicePoint': BusinessServicePoint,
#         'BspTypes': BspTypes,
#         'ContactEmbDoc': ContactEmbDoc
#     }
#
#     return render(request, 'market/console/bsp_edit.html', data)


@registered_user_only
@organization_console('market.businessservicepoint.change_businessservicepoint')
def console_bsp_edit_save(request, org, bsp_id):
    """
    API view to save edited bsp information.

    **Type**: POST

    **Authors**: Gagandeep Singh
    """
    if request.method.lower() == 'post':
        try:
            filters = copy.deepcopy(request.permissions['market.businessservicepoint']['data_access'])
            filters['organization_id'] = org.id
            filters['pk'] = bsp_id

            bsp = BusinessServicePoint.objects.get(**filters)
        except (TypeError, DoesNotExist_mongo):
            # TypeError: If filters is None
            return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message="You do not have permissions to edit this Business or Service Point.").gen_http_response()


        data = json.loads(request.POST.copy()['data'])
        form_bsp = BusinessServicePointForm(data, instance=bsp)

        if form_bsp.is_valid():
            form_bsp.save()
            return ApiResponse(status=ApiResponse.ST_SUCCESS, message='Ok.').gen_http_response()
        else:
            errors = dict(form_bsp.errors)
            return ApiResponse(status=ApiResponse.ST_FAILED, message='Please correct marked errors.', errors=errors).gen_http_response()
    else:
        # GET Forbidden
        return ApiResponse(status=ApiResponse.ST_FORBIDDEN, message='Use post.').gen_http_response()


@login_required
def partial_bsp_type_attributes(request, bsp_type):
    """
    Django view to return partial for a BSP type attributes.

    **Type**: GET

    **Authors**: Gagandeep Singh
    """
    try:
        bsp_type_class = MAPPING_BSP_CLASS[bsp_type]
    except KeyError:
        raise Http404("Invalid BSP type.")

    # Custom attributes
    if request.GET.get('c', None):
        try:
            #  'c' will automatically be checked in middleware
            org = Organization.objects.get(org_uid=request.GET['c'])
            custom_attr = BspTypeCustomization.objects.get(bsp_type=bsp_type, organization_id=org.id)
        except BspTypeCustomization.DoesNotExist:
            custom_attr = None
    else:
        custom_attr = None

    data = {
        "bsp_type_class_ENUMS": bsp_type_class.ENUMS,
        "custom_attr": custom_attr
    }

    if bsp_type == BspTypes.RESTAURANT:
        data['list_cuisines'] = RestaurantCuisine.objects.filter(active=True)

    return render(request, 'market/partials/bsp_types/{}_attributes.html'.format(bsp_type), data)

# --- /BusinessServicePoint ---

# ==================== /Console ====================


# ----- Custom API -----
@registered_user_only
@organization_console()
def api_search_org_bsp(request, org):
    """
    Custom API to search for organization BSP given query text. Query text must
    atleast 3 characters long.

    **Type**: GET

    **Filters**:

        - ``c``: (Mandatory) Organization UID
        - ``q``: Query text to be matched against name. Minimum of 3 characters
        - ``type``: (Optional) Type of BSP

    **Limit**: Maximum 10

    **Authors**: Gagandeep Singh
    """

    filters = {
        "organization_id": org.id
    }

    try:
        q = request.GET['q']
        if len(q) < 3:
            return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message="Query text 'q' must be 3 characters long.").gen_http_response()
        filters['name'] = re.compile(q, re.IGNORECASE)

        type_bsp = request.GET.get('type', None)
        if type_bsp:
            filters['type'] = type_bsp
    except KeyError:
        return ApiResponse(status=ApiResponse.ST_BAD_REQUEST, message="Missing parameters.").gen_http_response()


    result_aggr = BusinessServicePoint._get_collection().aggregate([
        {
            "$match": filters
        },
        {
            "$project":{
                "_id": 0,
                "id": "$_id",
                "name": 1
            }
        },
        {
            "$limit": 10
        }
    ])

    data = []
    for row in result_aggr:
        print row
        row['id'] = str(row['id'])
        data.append(row)

    return ApiResponse(status=ApiResponse.ST_SUCCESS, message="ok", objects=data).gen_http_response()


