# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
import json
import traceback

from mongoengine.queryset import DoesNotExist as DoesNotExist_mongo

from storeroom.models import ResponseQueue
from feedback import operations as ops_feedback
from surveys import operations as ops_surveys

class Command(BaseCommand):
    """
    Django management command to process form responses in queue(:class:`storeroom.models.ResponseQueue`)

    **Parameters:**

        - ``limit``: (Default 100) Number odfimports to be processed.


    Command::

        python manage.py storeroom_process_responses --limit 100

    **Authors**: Gagandeep Singh
    """
    help = "Command to migrate all imported BSP records to actual BSP."
    requires_system_checks = True
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            dest = "limit",
            help = "Limit size of responses to be processed. Default: 100",
            type = int,
            default = 100
        )

    # ----- Main executor -----
    def handle(self, *args, **options):
        limit = int(options['limit'])

        self.stdout.write(self.style.SUCCESS('Retrieving all pending responses (limit: {})...'.format(limit)))

        stats = {
            'count': 0,
            'ignored': 0,
            'failed': 0
        }
        for resp_queue in ResponseQueue.objects.filter(status=ResponseQueue.ST_NEW).limit(limit):

            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('\tProcessing: "{}"...'.format(resp_queue.pk)))

                # Change state to processing
                resp_queue.trans_process()
                resp_queue.save()

                try:
                    # Parse JSON data
                    data = json.loads(resp_queue.data)

                    # Perform operation as per the context of the response.
                    if resp_queue.context == ResponseQueue.CT_BSP_FEEDBACK:
                        # BSP Feedback Process
                        is_success = ops_feedback.save_bsp_feedback_response(data)
                    elif resp_queue.context == ResponseQueue.CT_SURVEY_RESPONSE:
                        # Survey response Process
                        is_success = ops_surveys.save_survey_response(data)
                    else:
                        raise NotImplementedError("Operation for '{}' response not implemented".format(resp_queue.context))

                    if is_success:
                        stats['count'] += 1
                    else:
                        stats['ignored'] += 1

                    # Delete Record
                    resp_queue.delete()

                except Exception as ex:
                    stats['failed'] += 1
                    self.stdout.write(self.style.SUCCESS('\t\tFailed: {}'.format(ex.message)))

                    traceback_text = traceback.format_exc()
                    resp_queue.trans_failed(ex.message, traceback_text)
                    resp_queue.save()


        self.stdout.write(self.style.SUCCESS('\nBatch completed! {}'.format(stats)))