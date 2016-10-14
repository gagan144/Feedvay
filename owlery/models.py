# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError

from django.utils import timezone
import re

# ---------- Validators ----------
def validate_sms_no(value):
    """
    Validator to check validity of a mobile number to which sms is to be send.

    Criteria: +<code: 1-4 digit><10-digit mobile number>

    :param value: Mobile number
    :return: None if valid else raises ValidationError.

    **Authors**: Gagandeep Singh
    """

    if re.match('^\+\d{1,4}\d{10}$', value) is None:
        raise ValidationError(
            _('%(value) is not an valid mobile number.'),
            params={'value': value},
        )
# ---------- /Validators ----------

class Sms(models.Model):
    """
    Model to store all SMS send to the users. This model act as a buffer/queue which is picked up
    by an independent process executing periodically at specific time interval. This is process reads
    unsent SMS from this model in a batch and dispatch them for sending. The result is then updated
    accordingly.

    **Authors**: Gagandeep Singh
    """

    # --- Enums ---
    ST_NEW = 'new'
    ST_SEND = 'send'
    ST_DELIVERED = 'delivered'
    ST_FAILED = 'failed'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_SEND, 'Send'),
        (ST_DELIVERED, 'Delivered'),
        (ST_FAILED, 'Failed')
    )

    TYPE_REG_VERIF = 'reg_verification'
    TYPE_REG_RESULT = 'reg_result'  # Result can by anything; success, failure, info etc
    CH_TYPE = (
        (TYPE_REG_VERIF, 'Registration Verification'),
        (TYPE_REG_RESULT, 'Registration Result')
    )

    PR_LOW = 'low'
    PR_NORMAL = 'normal'
    PR_HIGH = 'high'
    PR_URGENT = 'urgent'    # Will be send immediately
    CH_PRIORITY = (
        (PR_LOW, 'Low'),
        (PR_NORMAL, 'Normal'),
        (PR_HIGH, 'High'),
        (PR_URGENT, 'Urgent')
    )

    # --- Fields ---
    username    = models.CharField(max_length=255, null=True, blank=True, editable=False, db_index=True, help_text='User to whom this message is send. (Leave blank is not unknown)')
    mobile_no   = models.CharField(max_length=15, editable=False, db_index=True, validators=[validate_sms_no], help_text="Receiver's mobile number of E.164 format: +<code: 1-4 digits><10-digit mobile no> i.e +919999999999.")
    message     = models.TextField(max_length=150, editable=False, help_text='SMS text message.')

    type        = models.CharField(max_length=32, choices=CH_TYPE, editable=False, help_text='Type of this SMS.')
    priority    = models.CharField(max_length=16, choices=CH_PRIORITY, default=PR_NORMAL, help_text='Priority of this SMS.')

    status      = models.CharField(max_length=16, choices=CH_STATUS, default=ST_NEW, editable=False, db_index=True, help_text='Message status.')
    send_on     = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this SMS was successfully send.')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this SMS was created. This is NOT send date.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was updated.')

    class Meta:
        ordering = ('-created_on', )

    def __unicode__(self):
        return "{}".format(self.pk)


    def mark_send(self):
        self.status = Sms.ST_SEND
        self.send_on = timezone.now()
        self.save()

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Check status
        if self.status == Sms.ST_SEND and self.send_on is None:
            raise ValidationError('Please provide send date for this SMS.')

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


