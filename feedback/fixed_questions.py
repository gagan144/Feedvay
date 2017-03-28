# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from form_builder.fields import *
from form_builder.widgets import FieldWidgets
from languages.models import Translation

class BspFixedQuestions(object):
    questions = [
        RatingFormField(
            label = 'rating',
            text_translation_id = str(Translation.objects.get(unique_id='feedback-rating').pk),
            required = True,
            choice_type = MCQ_Types.INT,
            max_score = 5,
            widget = FieldWidgets.RATING_STARS
        ),
        TextAreaFormField(
            label = 'review',
            text_translation_id = str(Translation.objects.get(unique_id='feedback-write-review').pk),
            description = 'Please write your review',
            widget = FieldWidgets.HTML_TEXTAREA,
            ai_directives = None,
        )
    ]

    @staticmethod
    def to_json():
        jsn = [ques.to_json() for ques in BspFixedQuestions.questions]
        return jsn
