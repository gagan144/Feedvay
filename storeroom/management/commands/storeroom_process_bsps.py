# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from storeroom.models import ImportRecord
from clients.models import Organization
from market.models import BusinessServicePoint, BspTypeCustomization
from market.bsp_types import *
from utilities.abstract_models.mongodb import ContactEmbDoc, AddressEmbDoc


class Command(BaseCommand):
    """
    Django management command to migrate all imported BSP from storeroom(:class:`storeroom.models.ImportRecord`)
    to actual instances (:class:`market.models.BusinessServicePoint`).

    **Parameters:**

        - ``limit``: (Default 10) Number od imports to be processed.


    Command::

        python manage.py storeroom_process_bsps --limit 100

    **Authors**: Gagandeep Singh
    """
    help = "Command to migrate all imported BSP records to actual BSP."
    requires_system_checks = True
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            dest = "limit",
            help = "Limit size of records to be processed. Default: 10",
            type = int,
            default = 10
        )

    # ----- Main executor -----
    def handle(self, *args, **options):
        limit = int(options['limit'])

        self.stdout.write(self.style.SUCCESS('Retrieving pending BSP records (limit: {})...'.format(limit)))

        # Caches
        cache_org_bsptypecustm = {}   # Format: { "<org_id>__<bsp_type>": BspTypeCustomization, ... }

        count = 0
        for record in ImportRecord.objects.filter(context=ImportRecord.CNTX_BSP, status=ImportRecord.ST_NEW).limit(limit):
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('\tProcessing: "{}"...'.format(record.pk)))

                data = record.data_json

                try:
                    # ----
                    bsp_type = record.identifiers['bsp_type']
                    bsp_type_class = MAPPING_BSP_CLASS[bsp_type]

                    # Get BSP type customization if created
                    if record.organization_id:
                        lookup_key = '{}__{}'.format(record.organization_id, bsp_type)
                        bsp_custm = cache_org_bsptypecustm.get(lookup_key, None)
                        if bsp_type:
                            try:
                                bsp_custm = BspTypeCustomization.objects.get(organization_id=record.organization_id, bsp_type=bsp_type)
                                cache_org_bsptypecustm[lookup_key] = bsp_custm
                            except BspTypeCustomization.DoesNotExist:
                                bsp_custm = None

                    # Prepare data
                    dict_attributes = {}
                    dict_custom_attributes = {}
                    dict_contact = {}
                    dict_address = {}
                    dict_social = {}
                    for col_name, value in data.iteritems():
                        if col_name.startswith('attributes.'):
                            label = col_name.split('.')[1]
                            dict_attributes[label] = bsp_type_class.type_cast_value(label, value)
                        elif col_name.startswith('custom_attributes.') and bsp_custm:
                            label = col_name.split('.')[1]
                            dict_custom_attributes[label] = value
                        elif col_name.startswith('contacts.'):
                            label = col_name.split('.')[1]
                            dict_contact[label] = value
                        elif col_name.startswith('address.'):
                            label = col_name.split('.')[1]
                            dict_address[label] = value
                        elif col_name.startswith('social.'):
                            label = col_name.split('.')[1]
                            dict_social[label] = value


                    # Create BSP Type class instance for attributes
                    attributes = MAPPING_BSP_CLASS[bsp_type](dict_attributes)

                    # Create Custom attributes
                    if bsp_custm:
                        is_valid, error_msg = bsp_custm.validate_data(dict_custom_attributes)

                        if not is_valid:
                            raise Exception(error_msg)
                    else:
                        dict_custom_attributes = None

                    # Create contacts LIST (Optional)
                    if dict_contact.__len__():
                        list_contacts = [ContactEmbDoc(**dict_contact)]
                    else:
                        list_contacts = None

                    # Create address (Optional)
                    if dict_address.__len__():
                        address = AddressEmbDoc(**dict_address)
                    else:
                        address = None

                    # Create SocialMedia
                    social = BusinessServicePoint.SocialMedia(**dict_social)

                    # Finally Create BSP now
                    new_bsp = BusinessServicePoint.objects.create(
                        name = data['name'],
                        description = data.get('description', None),
                        type = bsp_type,

                        organization_id = record.organization_id,
                        brand_id = data.get('brand_id', None),
                        attributes = attributes.to_json(),
                        custom_attributes = dict_custom_attributes,

                        contacts = list_contacts,
                        address = None, # address,  #TODO: Address location_code
                        emails = data['emails'].split(',') if data.get('emails', None) else None,
                        website = data.get('website', None),

                        tags = data['tags'].split(',') if data.get('tags', None) else None,
                        social = social,
                        other_details = data.get('other_details', None),

                        created_by = record.created_by
                    )

                    # Remove record
                    record.delete()

                    self.stdout.write(self.style.SUCCESS('\t\tSuccess!'))

                    count += 1
                    # ---

                except Exception as ex:
                    # Migration failure
                    self.stdout.write(self.style.SUCCESS('\t\tFailed! {}'.format(ex.message)))

                    record.status = ImportRecord.ST_ERROR
                    record.error_message = ex.message
                    record.save()

        self.stdout.write(self.style.SUCCESS('\n{} BSP successfully migrated.'.format(count)))