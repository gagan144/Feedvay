# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save

from mongoengine.document import *
from mongoengine.fields import *

from django.contrib.auth.models import User

from clients.models import Organization
from market.models import BusinessServicePoint
from form_builder.models import Form, BaseResponse
from critics.models import Rating, Comment


# ========== BSP Feedback ==========
class BspFeedbackForm(Form):
    """
    Model to define a Business or Service Point feedback questionnaire for an organization.
    An organization can create any number of feedback questionnaire ad attach them to a
    BSP.

    This model inherits :class:`form_builder.models.Form` model since most of the properties for
    a feedback questionnaire are same, almost complete. At database layer, this means this table
    has unique foreign key to Form table, so for every 'BspFeedbackForm' there will be a 'Form'.
    All couple tables with 'Form' remains valid for this model also.

    **Points**:

        - Feedback questionnaire has no state cycle. They remain as free floating questionnaire.
          Any BSP attached to it uses this for displaying questionnaire form.
        - This nature allows few flexibilities:

            - All BSPs are not constrained to have common questionnaire. Different types of
              BSP or different categories of same BSP type can have different questionnaire.
              For example, restaurants for a state can have separate questionnaire tahn BSPs for some
              other state.
            - Also, this allows flexibility to change./update questionnaire as per need.

        - Hence, a feedback questionnaire is not directly accessible that means it is always accessed via
          BSP. The BSP defines what questionnaire to display as per the association.
        - Feedback has no specific audience. It is open to everyone.
        - Since BSPs can be associated to various questionnaires or a BSP might change its questions midway,
          this introduces some complexity in maintaining question uniqueness across questionnaires. It is likely to
          happen that for example; a question with label 'cleanliness' might be present in two questionnaires with
          slightly different context such as answer type. One can be a star rating, while other can be a multiple
          choice single select question. Whatever the case may be, while displaying a consolidated report, same label
          can have different type and answer values like in this case numeric and string.
        - So, any changes made in questions or questionnaire itself will not effect a BSP feedback response. Whatever
          was captures obsolete or not will be displayed.

    **Fields guidelines**:

        - ``title`` is although mandatory, but is not used in feedback. In this case, title will be used
          as name of the form for user usage only.
        - ``user_notes`` will be used to describe questionnaire for user own usage only.


    **Authors**: Gagandeep Singh
    """
    # --- Fields ---
    organization = models.ForeignKey(Organization, db_index=True, help_text='Organization to which this feedback form belongs to.')

    # tags        = models57.JSONField(blank=True, help_text='Name-Value pair dictionary of tags for this form.')
    created_by  = models.ForeignKey(User, editable=False, help_text='User that created this feedback questionnaire.')

    class Meta:
        permissions = (
            ("view_bspfeedbackform", "Can view BSP feedback questionnaire"),
        )

    def get_attached_bsps(self):
        """
        Method to return all BSPs attached to this feedback form.

        :return: List<:class:`market.models.BusinessServicePoint`>
        """
        from market.models import BusinessServicePoint
        # return BusinessServicePoint.objects.filter(feedback_form_id=self.id)
        return BusinessServicePoint.objects.filter(feedback_form__form_id=self.id)

    def delete(self, using=None, keep_parents=False):
        raise ValidationError("You cannot delete BSP feedback questionnaire.")
post_save.connect(BspFeedbackForm.post_save, sender=BspFeedbackForm)


class BspFeedbackResponse(BaseResponse):
    """
    Model to store BSP feedback response. It inherits all properties of :class:`form_builder.models.BaseResponse`.

    **Flow for BSP Feedback Response save**:

        .. image:: ../../_static/feedback/bsp_response_save_flow.jpg


    **Authors**: Gagandeep Singh
    """
    bsp_id      = StringField(required=True, help_text='BSP ID for which feedback was made.')

    rating_id   = StringField(required=True, help_text='Instance ID of :class:`critics.models.Rating`')
    comment_id  = StringField(help_text='(Optional) Instance ID of :class:`critics.models.Comment`.')

    meta = {
        'indexes':[
            'bsp_id',
        ]
    }

    @property
    def bsp(self):
        return BusinessServicePoint.objects.get(pk=self.bsp_id)

    @property
    def form(self):
        return BspFeedbackForm.objects.get(id=self.form_id)

    @property
    def rating(self):
        return Rating.objects.with_id(self.rating_id)

    @property
    def comment(self):
        return Comment.objects.with_id(self.comment_id) if self.comment_id else None

# ========== /BSP Feedback ==========
