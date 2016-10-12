# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

from django.contrib.auth.models import User

class RegisteredUser(models.Model):
    """
    Extension of django :class:`django.contrib.auth.models.User` model that maintains all public user
    information. For every public user, a record is created with reference to 'User' model along with
    other attributes such as mode of registration, user personal settings etc.

    **Points**:
        - This model does not include any staff users.
        - Username of these users is the mobile phone no with country code as prefix. Example: +919999999999
        - All login related process such as session allocation etc are done using traditional django 'User' model whereas
          other business related functionality are done using this model.
        - Detailed personal information are not kept in this model. It only contains basic information only such as name, email id.
        - Registration methods:
            - **Website**: User can register directly on website using mobile no.
            - **Mobile app**: User can register using mobile app.
            - **Enterprise app**: Passive registration of the user that is automatically created as a **lead** while using enterprise app.
              The account remains inactive until user register himself manually using any of the methods.

            For registration flow, refer the document.
        - Registration can be multiple times. Only last registration information is kept for now.

    .. warning::
        This model must not trigger any update to django 'User' model since it can trigger model's save.
        However, you can update this model without any intervention of 'User' model.

    **Authors**: Gagandeep Singh
    """

    # ----- enums -----
    REG_WEB_PORTAL = 'web_portal'
    REG_MOBILE = 'mobile_app'
    REG_CAPTURED_LEAD = 'captured_lead' # User was captured as lead while from enterprise app.
    CH_REG_METHOD = (
        (REG_WEB_PORTAL, 'Web portal'),
        (REG_MOBILE, 'Mobile app'),
        (REG_CAPTURED_LEAD, 'Captured lead'),
    )

    ST_LEAD = 'lead'
    ST_VERIFICATION_PENDING = 'verification_pending'
    ST_VERIFIED = 'verified'

    # ----- fields -----
    user        = models.OneToOneField(User, db_index=True, editable=False, help_text='Reference to django user model.')
    reg_method  = models.CharField(max_length=32, choices=CH_REG_METHOD, db_index=True, editable=False, help_text='Last registration method used by the user')
    reg_count   = models.SmallIntegerField(default=1, editable=False, help_text='No of times this user registered himself.')
    last_reg_date = models.DateTimeField(auto_now_add=True, editable=False, help_text='Last registration datetime.')
    status      = FSMField(default=ST_LEAD, protected=True, db_index=True, editable=False, help_text='Status of user registration.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this suggestion was made.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('-created_on', )

    # ----- Transitions -----
    @fsm_log_by
    @transition(field=status, source=[ST_LEAD, ST_VERIFIED], target=ST_VERIFICATION_PENDING)
    def trans_registered(self):
        """
        User has registered. Status is transitioned from ``lead`` to ``verification_pending``.
        """
        pass

    @fsm_log_by
    @transition(field=status, source=ST_VERIFICATION_PENDING, target=ST_VERIFIED)
    def trans_verification_completed(self):
        """
        User has verified himself. Status is transitioned from ``verification_pending`` to ``verified``.
        """
        pass

    # ----- /Transitions -----

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

