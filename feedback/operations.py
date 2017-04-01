# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.utils import timezone

from django.contrib.auth.models import User

from market.models import BusinessServicePoint
from feedback.models import BspFeedbackForm, BspFeedbackResponse
from critics.models import Entities, Rating, Comment

def save_bsp_feedback_response(response_json):
    """
    Method to save BSP Feedback Response.

    :param response_json: JSON dict data that has to be processed.
    :return: True if processing was successful, False if response was already processed.

    .. warning::
        This method throws exception and must be handled accordingly.

    **Authors**: Gagandeep Singh
    """
    # Get concerned BSP
    bsp_id = response_json['bsp_id']
    bsp = BusinessServicePoint.objects.with_id(bsp_id)

    # Get BSP Feedback form
    form_id = response_json['form_id']
    form = BspFeedbackForm.objects.get(id=form_id)
    form_version = response_json['form_version']
    version_obsolete = False if str(form.version) == form_version else True

    # Get User who made this feedback
    user_id = response_json['user']['user_id']
    user = User.objects.get(id=user_id)

    # Check if this response has already been processed
    response_uid = response_json['response_uid']
    response_date = timezone.datetime.strptime(response_json['response_date'],"%Y-%m-%dT%H:%M:%S")
    if not BspFeedbackResponse.objects.filter(response_uid=response_uid).count():
        # Begin processing

        # (a) Extract Rating and Review from ``response_json.answers`` and delete them
        rating = int(response_json['answers']['rating'])
        del response_json['answers']['rating']

        review = response_json['answers'].get('review', None)
        if review:
            del response_json['answers']['review']

        # (b) Save Rating
        Rating.objects.create(
            content_type = Entities.BSP,
            object_id   = str(bsp.pk),
            rating      = rating,
            user_id     = user.id,
            dated       =  response_date
        )

        # (c) Save comment/review
        if review not in [None, '']:
            Comment.objects.create(
                content_type = Entities.BSP,
                object_id   = str(bsp.pk),
                text        = review,
                # ai_pending  = # TODO: Check if AI is to be applied?
                # ai          = {}
                user_id     = user.id,
                dated       = response_date
            )

        # (d) Create BSP Feedback Response
        bsp_response = BspFeedbackResponse.objects.create(
            bsp_id          = str(bsp.pk),
            form_id         = str(form.id),
            form_version    = form_version,
            version_obsolete = version_obsolete,

            app_version     = response_json['app_version'],
            user            = BspFeedbackResponse.UserInformation(**response_json['user']) if response_json['user'] else None,
            end_point_info  = BspFeedbackResponse.EndPointInformation(**response_json['end_point_info']),
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

            location        = BspFeedbackResponse.LocationInformation(**response_json['location']) if response_json['location'] else None,

            flags           = BspFeedbackResponse.ResponseFlags(
                                   description_read = response_json['flags']['description_read'],
                                   instructions_read = response_json['flags']['instructions_read'],
                                   suspect = response_json['flags']['suspect'],
                                   suspect_reasons = response_json['flags']['suspect_reasons']
                              )
        )

        # Processing completed! Return now
        return True
    else:
        # Already processed: Ignore
        return False