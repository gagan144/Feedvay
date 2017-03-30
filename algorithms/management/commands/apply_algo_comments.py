# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from critics.models import Comment
from algorithms.text import *

class Command(BaseCommand):
    """
    Django management command to apply all algorithms on comments which are yet not processed.

    Command::

        python manage.py apply_algo_comments

    **Authors**: Gagandeep Singh
    """
    help = "Apply all algorithms on pending comments."
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

        self.stdout.write(self.style.SUCCESS('Retrieving pending Comments (limit: {})...'.format(limit)))

        # Get all pending survey responses
        list_comments = Comment.objects.filter(ai_pending=True)[:limit]

        summary = {
            'total': 0,
        }
        for comment in list_comments:
            self.stdout.write(self.style.SUCCESS("Processing comment '{}' ...".format(comment.pk)))

            if comment.ai:
                # Get all pending keys
                list_algo_keys = [key for key,data in comment.ai.iteritems() if data.get('pending', False)]

                # Call all algorithms at once
                ta_results = analyse_text(comment.text, list_algo_keys)

                # Update results
                for algo_key, algo_result in ta_results.iteritems():
                    comment.ai[algo_key]['result'] = algo_result
                    comment.ai[algo_key]['pending'] = False

                # Set ai_pending as None
                comment.ai_pending = None

                # Save
                comment.save()

                summary['total'] += 1


        self.stdout.write(self.style.SUCCESS("\n----------\nDone!\n{summary}\n----------".format(summary=summary)))
