# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from owlery.models import *

class SmsOwl:
    """
    Owl to handle all sms. This class defines various SMS templates that can be send in an **asynchronous**
    manner.

    Following is the complete SMS workflow:
        1. Call any of the defined handler methods with required parameters.
        2. The method uses parameters to compose a message and creates database entry.
        3. An independent process running periodically picks up this message as per its priority
           and sends the message.

    .. note:
        SMS are not send immediately as one synchronized call. There will be some delay which increases
        as priority decreases.

    **Authors**: Gagandeep Singh
    """

    @staticmethod
    def send_reg_verification(mobile_no, user_token, username=None):
        """
        Sends a SMS containing OTP for registration verification.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param user_token: Instance of :class:`accounts.models.UserToken` containing the otp.
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        message_body = render_to_response('owlery/owls/sms/reg_verification.txt',{
            "otp": user_token.value,
            "expire_time": user_token.expire_on.time().strftime("%H:%M:%S")     #TODO: Timezone: convert to local
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_REG_VERIF,
            priority = SmsMessage.PR_URGENT
        )

        return sms