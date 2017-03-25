# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_mysql import models as models57
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

from clients.models import Organization
from market.models import BusinessServicePoint
from form_builder.models import Form


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

    def delete(self, using=None, keep_parents=False):
        raise ValidationError("You cannot delete BSP feedback questionnaire.")


class BspFeedbackAssociation(models.Model):
    """
    Model to associate a :class:`market.models.BusinessServicePoint` to a :class:`feedback.models.BspFeedbackForm`.

    At a given instance of time, a BSP can be associated with only on feedback form.

    **Authors**: Gagandeep Singh
    """
    bsp_id  = models.CharField(max_length=64, db_index=True, help_text="BusinessServicePoint ID which is being associated.")
    form    = models.ForeignKey(BspFeedbackForm, db_index=True, help_text='Bsp Feedback form to be associated to BSP.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this record was created.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def bsp(self):
        return BusinessServicePoint.objects.get(pk=self.bsp_id)

    class Meta:
        unique_together = ('bsp_id', 'form')
        permissions = (
            ("view_bspfeedbackassociation", "Can associate BSP with feedback questionnaire"),
        )

    def __unicode__(self):
        return "{} - {}".format(self.form.title, self.bsp_id)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, update_theme=False, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


# ========== /BSP Feedback ==========