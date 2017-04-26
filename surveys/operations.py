# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.utils import timezone

from django.contrib.auth.models import User
from surveys.models import Survey, SurveyResponse

def save_survey_response(response_json):
    """
    Method to save survey response.

    :param response_json: JSON dict data that has to be processed.
    :return: True if processing was successful, False if response was already processed.

    **Note**:

        - Currently only registered users are allowed to submit response

    .. warning::
        This method throws exception and must be handled accordingly.

    **Authors**: Gagandeep Singh
    """
    # Bring out regular variables
    response_uid = response_json['response_uid']
    form_version = response_json['form_version']

    # Fetch survey, phase, form as per the survey uid
    survey = Survey.objects.get(survey_uid=response_json['survey_uid'])
    phase = survey.phases.get(id=response_json['phase_id'])
    form = phase.form

    version_obsolete = False if str(form.version) == form_version else True

    # Get User who submitted this response
    user_id = response_json['user']['user_id']
    user = User.objects.get(id=user_id)

    # Check if response is already created
    if not SurveyResponse.objects.filter(response_uid=response_uid).count():
        # Create new entry
        survey_response = SurveyResponse.objects.create(
            survey_uid      = str(survey.survey_uid),
            phase_id        = str(phase.id),
            form_id         = str(form.id),
            form_version    = form_version,
            version_obsolete = version_obsolete,

            app_version     = response_json['app_version'],
            user            = SurveyResponse.UserInformation(**response_json['user']) if response_json['user'] else None,
            end_point_info  = SurveyResponse.EndPointInformation(**response_json['end_point_info']),
            language_code   = response_json["language_code"],

            response_uid    = response_uid,
            constants       = response_json.get('constants', None),
            answers         = response_json['answers'],
            answers_other   = response_json['answers_other'],
            calculated_fields = response_json['calculated_fields'],

            timezone_offset = response_json['timezone_offset'],
            response_date   = timezone.datetime.strptime(response_json['response_date'],"%Y-%m-%dT%H:%M:%S"),
            start_time      = timezone.datetime.strptime(response_json['start_time'],"%Y-%m-%dT%H:%M:%S"),
            end_time        = timezone.datetime.strptime(response_json['end_time'],"%Y-%m-%dT%H:%M:%S"),
            duration        = response_json['duration'],

            location        = SurveyResponse.LocationInformation(**response_json['location']) if response_json['location'] else None,

            flags           = SurveyResponse.ResponseFlags(
                                   description_read = response_json['flags']['description_read'],
                                   instructions_read = response_json['flags']['instructions_read'],
                                   suspect = response_json['flags']['suspect'],
                                   suspect_reasons = response_json['flags']['suspect_reasons']
                              )
        )

        # Processing completed! Return now
        return True
    else:
        # Response has already been processed; Ignore
        return False
