# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from surveys.models import SurveyResponse
from algorithms.text import *

class Command(BaseCommand):
    """
    Django management command to apply all algorithms on pending surveys responses.

    **Authors**: Gagandeep Singh
    """
    help = "Apply all algorithms on pending survey responses."
    requires_system_checks = True
    can_import_settings = True

    # ----- Main executor -----
    def handle(self, *args, **options):
        # Get all pending survey responses
        list_responses = SurveyResponse.objects.filter(process_flags__text_analysis=True)[:1]


        summary = {
            'total': 0,
            'text_analyis': 0
        }
        for response in list_responses:
            # --- Response ---
            self.stdout.write(self.style.SUCCESS("Processing survey response '{}' ...".format(response.pk)))

            # --- Text analysis ---
            if response.process_flags.text_analysis:
                self.stdout.write(self.style.SUCCESS("\tApplying text analysis:"))

                # For all answers which are to be analysed
                for answer in response.list_answers:
                    if answer.ai:
                        self.stdout.write(self.style.SUCCESS("\t\t'{}' ...".format(answer.question_label)))

                        # Get all pending keys
                        list_algo_keys = [key for key,data in answer.ai.iteritems() if data.get('pending', False)]

                        # Call all algorithms at once
                        ta_results = analyse_text(answer.answer, list_algo_keys)

                        # Update results
                        for algo_key, algo_result in ta_results.iteritems():
                            answer.ai[algo_key]['result'] = algo_result
                            answer.ai[algo_key]['pending'] = False

                # Remove process_flags.text_analysis
                response.process_flags.text_analysis = None

                # Save
                print response.process_flags.text_analysis
                print response.list_answers[8].ai
                response.save()

                # Update summary
                summary['text_analyis'] += 1
            # --- /Text analysis ---

            summary['total'] += 1
            # --- /Response ---

        self.stdout.write(self.style.SUCCESS("\n----------\nDone!\n{summary}\n----------".format(summary=summary)))
