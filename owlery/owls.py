# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
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
        SMS may not be send immediately as a single synchronized call. There will be some delay which increases
        as priority decreases.

    **Authors**: Gagandeep Singh
    """

    @staticmethod
    def send_reg_verification(mobile_no, user_token, username=None):
        """
        Sends a 'registration verification' SMS containing verification code.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param user_token: Instance of :class:`accounts.models.UserToken` containing the code.
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        message_body = render_to_response('owlery/owls/sms/reg_verification.txt',{
            "code": user_token.value,
            "expire_time": user_token.humanize_expire_on("%I:%M %p")
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_REG_VERIF,
            priority = SmsMessage.PR_URGENT
        )

        return sms

    @staticmethod
    def send_password_reset(mobile_no, user_token, username=None):
        """
        Sends a 'password reset/recovery' SMS containing verification code.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param user_token: Instance of :class:`accounts.models.UserToken` containing the code.
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        message_body = render_to_response('owlery/owls/sms/password_reset.txt',{
            "code": user_token.value,
            "expire_time": user_token.humanize_expire_on("%I:%M %p")
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_PASS_RESET,
            priority = SmsMessage.PR_URGENT
        )

        return sms


class EmailOwl:
    """
    Owl to handle all emails. This class defines various email template that can used to send email.
    All methods composes email according to the parameters and store them in :class:`owlery.models.EmailMessage`
    from where they are picked up by a cron process for dispatching.

    .. note:
        Emails may not be send immediately. There will be some delay which increases as priority decreases.

    **Authors**: Gagandeep Singh
    """

    @staticmethod
    def send_password_reset(email_address, user_token, username=None):
        """
        Sends a 'password reset/recovery' email containing verification code.

        :param email_address: Email address of the receiver
        :param user_token: Instance of :class:`accounts.models.UserToken` containing the code.
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.EmailMessage` instance.

        .. note:
            This method sends email immediately. In case of failure, message remains in the queue.

        **Authors**: Gagandeep Singh
        """

        receiver_name = None
        if username:
            user = User.objects.get(username=username)
            receiver_name = "{} {}".format(user.first_name, user.last_name)

        # Create message body
        message_body = render_to_response('owlery/owls/emails/password_reset.html', {
            "receiver_name": receiver_name,
            "code": user_token.value,
            "expire_min": (settings.VERIFICATION_EXPIRY/60),
            "expire_time": user_token.humanize_expire_on("%I:%M %p")
        }).content

        # Create database entry
        email_msg = EmailMessage.objects.create(
            username = username,
            email_id = email_address,

            subject = "Feedvay Account - {} is your recovery verification code".format(user_token.value),
            message = message_body,

            type = EmailMessage.TYPE_PASS_RESET,
            priority = EmailMessage.PR_URGENT
        )

        # Send email since it is an urgent message
        try:
            email_msg.force_send()
        except:
            pass

        return email_msg