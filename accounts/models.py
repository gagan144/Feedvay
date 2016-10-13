# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
import random
import string

from django.conf import settings
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
            - **Website** (Only one time): User can register directly on website using mobile no.
            - **Mobile app** (Multiple times): User can register using mobile app.
            - **Enterprise app** (Only one time): Passive registration of the user that is automatically created as a **lead** while using enterprise app.
              The account remains inactive until user register himself manually using any of the methods. Only one time record is created
              and ignore in further cases.

            For registration flow, refer the document.
        - Registration can be multiple times. Only last registration information is kept for now.

    **State chart diagram for state machine**:
        .. image:: ../../_static/accounts/registereduser_statechart.jpg

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

    def __unicode__(self):
        return self.user.username

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

class UserToken(models.Model):
    """
    Model to store tokens issued to a registered user for various purposes such as registration.

    **Points**:
        - Uniqueness of a token is based on :class:`accounts.model.RegisteredUser` and purpose.
        - Tokens are only issued to registered user.
        - Token can be overridden for same user & purpose. This is possible when the same process is again executed.
        - No audit trail is maintained for a token. Present is the only truth.
        - Token must be deleted after use or will be automatically deleted after they cross their expiry date.

    .. note::
        Tokens are not user sessions.

    **Authors**: Gagandeep Singh
    """

    PUR_OTP_VERF = 'otp_verification'
    CH_PURPOSE = (
        (PUR_OTP_VERF, 'OTP Verification'),
    )

    registered_user = models.ForeignKey(RegisteredUser, db_index=True, editable=False, help_text='Reference to the registered user to whom this token belongs.')
    purpose     = models.CharField(max_length=64, choices=CH_PURPOSE, db_index=True, editable=False, help_text='Purpose for which this token is issued')

    value       = models.CharField(max_length=512, editable=False, help_text='Value of the token')
    expire_on   = models.DateTimeField(editable=False, db_index=True, help_text='Date after which this token will expire.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, help_text='Date on which this token was issued.')

    def __unicode__(self):
        return "{} - {}".format(self.registered_user.user.username, self.purpose)

    class Meta:
        unique_together = ('registered_user', 'purpose')

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Set expiry date
        if self.purpose == UserToken.PUR_OTP_VERF:
            self.value = UserToken.gen_verification_otp()
            self.expire_on = timezone.now() + timezone.timedelta(seconds=settings.VERIFICATION_EXPIRY)

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """

        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    @staticmethod
    def gen_verification_otp():
        charset = string.digits
        return ''.join(random.sample(charset,6))




# ----- Global Methods -----
def set_user_password(user, new_password, send_owls=True):
    """
    Method to set a user password and save it.
    This also sends any owls (Email or SMS) if required. Any errors are silently ignored.

    :param user: 'User' model object
    :param new_password: New password
    :param send_owls: Set True to send mail/SMS to the user. Default:True
    :return: None

    .. note::
        To prevent logout, execute following after this function.

            >>> auth.update_session_auth_hash(request, user)


    **Authors**: Gagandeep Singh
    """
    user.set_password(new_password)
    user.save()

    # if send_mail and settings.MAIL_PASS_RESET_SUCCESS:
    #     try:
    #         result = mailing.send_password_reset_success_email(user)
    #     except SMTPAuthenticationError:
    #         pass
    #     except:
    #         pass

