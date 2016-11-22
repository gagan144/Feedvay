# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from owlery.models import SmsMessage, EmailMessage, NotificationMessage, NotificationRecipient

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

        # TODO: Send SMS immediately using gateway

        return sms


    @staticmethod
    def send_password_change_success(mobile_no, username=None):
        """
        Sends a password change success SMS to the user.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        message_body = render_to_response('owlery/owls/sms/password_change_success.txt',{
            "change_date": timezone.now().strftime("%I:%M %p"),
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_PASS_CHNG_SUCC,
            priority = SmsMessage.PR_HIGH
        )

        # TODO: Send SMS immediately using gateway

        return sms


    @staticmethod
    def send_brand_disassociation_success(mobile_no, brand, username=None):
        """
        Sends a SMS confirmation to the user about his disassociation from the brand.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param brand: :class:`brands.models.Brand` model instance
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        message_body = render_to_response('owlery/owls/sms/brand_disassociation_success.txt',{
            "brand_name": brand.name
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_BRAND_DISASS_SUCC,
            priority = SmsMessage.PR_HIGH
        )

        # TODO: Send SMS immediately using gateway

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

    @staticmethod
    def send_password_change_success(user):
        """
        Sends password change success email to the user.

        :param user: User instance to whom email is to be send
        :return: Returns :class:`owlery.model.EmailMessage` instance if email address was present else None

        .. note::
            Email is send immediately.

        **Authors**: Gagandeep Singh
        """

        email_address = user.email

        if email_address is not None and email_address != '':
            receiver_name = "{} {}".format(user.first_name, user.last_name)

            # Create message body
            message_body = render_to_response('owlery/owls/emails/password_change_success.html', {
                "username": user.username,
                "receiver_name": receiver_name,
                "dated": timezone.now()
            }).content

            # Create database entry
            email_msg = EmailMessage.objects.create(
                username = user.username,
                email_id = email_address,

                subject = "Feedvay - Account password successfully changed",
                message = message_body,

                type = EmailMessage.TYPE_PASS_CHNG_SUCC,
                priority = EmailMessage.PR_HIGH
            )

            # Send email since it is an urgent message
            try:
                email_msg.force_send()
            except:
                pass

            return email_msg

        else:
            # Email not found in user, ignore and return None
            return None

    @staticmethod
    def send_brand_disassociation_success(user, brand):
        """
        Sends confirmation email to user' disassociation from a brand.

        :param user: User instance to whom email is to be send
        :param brand: :class:`brands.models.Brand` model instance
        :return: Returns :class:`owlery.model.EmailMessage` instance if email address was present else None

        .. note::
            Email is send immediately.

        **Authors**: Gagandeep Singh
        """

        email_address = user.email

        if email_address is not None and email_address != '':
            receiver_name = "{} {}".format(user.first_name, user.last_name)

            # Create message body
            message_body = render_to_response('owlery/owls/emails/brand_disassociation_success.html', {
                "username": user.username,
                "receiver_name": receiver_name,
                "brand": brand,
                "dated": timezone.now()
            }).content

            # Create database entry
            email_msg = EmailMessage.objects.create(
                username = user.username,
                email_id = email_address,

                subject = "Feedvay - Brand disassociation confirmation",
                message = message_body,

                type = EmailMessage.TYPE_BRAND_DISASS_SUCC,
                priority = EmailMessage.PR_URGENT
            )

            # Send email since it is an urgent message
            try:
                email_msg.force_send()
            except:
                pass

            return email_msg

        else:
            # Email not found in user, ignore and return None
            return None

    @staticmethod
    def send_brand_partner_left_message(brand, reg_user_disass):
        """
        Sends an email to all brand owners about a partner's disassociation.
        At this point user has left brand.

        :param brand: :class:`brands.models.Brand` model instance
        :param reg_user_disass: Registered user instance that left the brand
        :return: Returns List<:class:`owlery.model.EmailMessage` instance> of those owners who had email address.

        **Authors**: Gagandeep Singh
        """

        left_user = reg_user_disass.user
        left_user_name = "{} {}".format(
            left_user.first_name,
            left_user.last_name
        )

        list_emails = []
        for owner in brand.owners.all():
            user_owner = owner.user
            email_address = user_owner.email

            if email_address is not None and email_address != '':
                receiver_name = "{} {}".format(user_owner.first_name, user_owner.last_name)

                # Create message body
                message_body = render_to_response('owlery/owls/emails/brand_partner_left.html', {
                    "receiver_name": receiver_name,
                    "left_user": left_user,
                    "brand": brand,
                    "dated": timezone.now()
                }).content

                # Create database entry
                email_msg = EmailMessage.objects.create(
                    username = user_owner.username,
                    email_id = email_address,

                    subject = "Feedvay - {} left brand ownership".format(left_user_name),
                    message = message_body,

                    type = EmailMessage.TYPE_BRAND_PARTNER_LEFT,
                    priority = EmailMessage.PR_NORMAL
                )

                list_emails.append(email_msg)

        return list_emails


class NotificationOwl:
    """
    Owl to handle all notification that can be send in an **asynchronous** manner to all devices (mobile or web) of a user.

    Following is the complete notification workflow:

        1. Call any of the defined handler methods with required parameters.
        2. The method uses parameters to compose a message and creates database entry.
        3. An independent process running periodically picks up this message as per its priority
           and sends the message to push service.

    .. note:
        Notifications may not be send immediately as a single synchronized call. There will be some delay which increases
        as priority decreases.

    **Authors**: Gagandeep Singh
    """

    @staticmethod
    def send_brand_partner_left_notif(brand, reg_user_disass):
        """
        Sends notifications to all brand owners about a partner's disassociation.
        At this point user has left brand.

        :param brand: :class:`brands.models.Brand` model instance
        :param reg_user_disass: Registered user instance that left the brand
        :return: Returns :class:`owlery.model.NotificationMessage` instance, None if there are no owners of the brand


        **Authors**: Gagandeep Singh
        """

        left_user = reg_user_disass.user
        left_user_name = "{} {}".format(
            left_user.first_name,
            left_user.last_name
        )

        if brand.owners.all().count():
            with transaction.atomic():
                # Create message body
                message_body = render_to_response('owlery/owls/notifications/brand_partner_left.html', {
                    "left_user_name": left_user_name,
                    "brand": brand,
                }).content

                # Create entry
                notif_msg = NotificationMessage.objects.create(
                    target = NotificationMessage.TARGET_USER,
                    transmission = NotificationMessage.TRANSM_UNICAST,
                    type = NotificationMessage.TYPE_BRAND_PARTNER_LEFT,
                    message = message_body,
                    url_web = "/console/b/{}/settings/#/ownership".format(brand.brand_uid),
                    priority = NotificationMessage.PR_HIGH
                )

                # Create recipients in bulk
                NotificationRecipient.objects.bulk_create([
                    NotificationRecipient(
                        notif_message = notif_msg,
                        registered_user = owner
                    ) for owner in brand.owners.all()
                ])

                return notif_msg
        else:
            return None