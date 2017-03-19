# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
import shapefile
from geojson import Polygon

from mongoengine.queryset import DoesNotExist as DoesNotExist_mongo

from storeroom.models import ImportRecord
from geography.models import *
from geography.utilities import generate_fulladdr_from_path


class Command(BaseCommand):
    """
    Django management command to migrate all imported geolocation records to GeoLocation collection.

    **Parameters:**

        - ``limit``: (Default 100) Number od imports to be processed.


    Command::

        python manage.py storeroom_process_geolocations --limit 1000

    **Authors**: Gagandeep Singh
    """
    help = "Command to migrate all imported geolocation records to actual GeoLocation collection."
    requires_system_checks = True
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            dest = "limit",
            help = "Limit size of records to be processed. Default: 100",
            type = int,
            default = 100
        )

    # ----- Main executor -----
    def handle(self, *args, **options):
        limit = int(options['limit'])

        self.stdout.write(self.style.SUCCESS('Retrieving pending geolocation records (limit: {})...'.format(limit)))

        # Caches
        cache_shp_files = {}     # Format: { "<shape file path>": <shp object>, ... }

        count_created = 0
        count_failed = 0
        for record in ImportRecord.objects.filter(context=ImportRecord.CNTX_GEO_LOC, status=ImportRecord.ST_NEW).limit(limit):
            with transaction.atomic():
                data = record.data_json
                self.stdout.write(self.style.SUCCESS('\tProcessing: "{} - {}"...'.format(record.pk, data['name'])))

                try:
                    # Add full address as per path
                    data["hierarchies"]["full_address"] = generate_fulladdr_from_path(data["hierarchies"]["path"])

                    update_dict = {
                        "set__code_iso": data.get("code_iso", None),
                        "set__name": data["name"],
                        "set__division_type": data["division_type"],
                        "add_to_set__hierarchies": [data["hierarchies"]],    # Just one hierarchy doc
                        "set__post_office": data.get("post_office", None),
                        "set__centroid": data.get("centroid", None),
                        "add_to_set__data_sources": data["data_sources"],
                        "set__dated": timezone.datetime.strptime(data["dated"], "%Y-%m-%dT%H:%M:%S"),

                        "upsert": True
                    }

                    if data.get("names_alias", None):
                        update_dict["add_to_set__names_alias"] = data["names_alias"].split(",")
                    if data.get("data_sources", None):
                        update_dict["add_to_set__data_sources"] = data["data_sources"].split(",")



                    if data.get('shape_id', None):
                        shape_id = data['shape_id']
                        shp_file_path = data['shape_file_path']

                        # Load shape file
                        shp_file = cache_shp_files.get(shp_file_path, None)
                        if shp_file is None:
                            shp_file = shapefile.Reader(shp_file_path)
                            cache_shp_files[shp_file_path] = shp_file

                        # Get shape
                        poly = shp_file.shapeRecords()[shape_id].shape.points

                        update_dict['set__shape'] = Polygon([poly])

                    # Upsert
                    GeoLocation.objects(
                        code = data['code']
                    ).update_one(
                        **dict(update_dict)
                    )

                    # Remove record
                    record.delete()

                    self.stdout.write(self.style.SUCCESS('\t\tSuccess!'))

                    count_created += 1

                except Exception as ex:
                    # Migration failure
                    self.stdout.write(self.style.SUCCESS('\t\tFailed! {}'.format(ex.message)))
                    count_failed += 1

                    record.status = ImportRecord.ST_ERROR
                    record.error_message = ex.message
                    record.save()

        self.stdout.write(self.style.SUCCESS('\nCompleted! {} Migrated, {} Failed.'.format(count_created, count_failed)))