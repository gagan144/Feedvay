# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.urlresolvers import reverse

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
    def send_org_invitation(mobile_no, org_mem, reg_user_created, username=None):
        """
        Sends a organization invitation SMS.

        :param mobile_no: Mobile number. +91-9999999999 is converted to +919999999999
        :param org_mem: Membership instance :class:`clients.models.OrganizationMember`
        :param reg_user_created: If True, it means invitee was created during invitation.
        :param username: (Optional) Username of user to which SMS is to be send.
        :return: Returns :class:`owlery.model.SmsMessage` instance.

        **Authors**: Gagandeep Singh
        """

        template_name = 'org_invitation_new.txt' if reg_user_created else 'org_invitation.txt'
        message_body = render_to_response('owlery/owls/sms/'+template_name,{
            "org_mem": org_mem,
        }).content

        sms = SmsMessage.objects.create(
            username = username,
            mobile_no = mobile_no.replace('-',''),
            message = message_body,
            type = SmsMessage.TYPE_ORG_INVTN,
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
    def send_email_verification(reg_user, user_token, verif_url, email_address):
        """
        Method to send a verification link to newely added email address.

        :param reg_user: RegisteredUser to whom email is send
        :param user_token: User token for email verification
        :param verif_url: Verification url
        :param email_address: New email address to which link is to be send
        :return: Returns :class:`owlery.model.EmailMessage` instance

        **Authors**: Gagandeep Singh
        """
        user = reg_user.user
        receiver_name = "{} {}".format(user.first_name, user.last_name)

        # Create message body
        message_body = render_to_response('owlery/owls/emails/email_verification.html', {
            "receiver_name": receiver_name,
            "url": verif_url,
            "expire_min": (settings.VERIFICATION_EXPIRY/60),
            "expire_time": user_token.humanize_expire_on("%I:%M %p")
        }).content

        # Create database entry
        email_msg = EmailMessage.objects.create(
            username = user.username,
            email_id = email_address,

            subject = "Feedvay - Email verification",
            message = message_body,

            type = EmailMessage.TYPE_EMAIL_VERIF,
            priority = EmailMessage.PR_URGENT
        )

        # Send email since it is an urgent message
        try:
            email_msg.force_send()
        except:
            pass

        return email_msg

    @staticmethod
    def send_org_invitation(org_mem):
        """
        Method to send a organization invitation email.

        :param org_mem: Membership instance :class:`clients.models.OrganizationMember`
        :return: Returns :class:`owlery.model.EmailMessage` instance

        **Authors**: Gagandeep Singh
        """

        user  = org_mem.registered_user.user
        url = "{domain}{url}?c={org_uid}".format(
            domain = settings.FEEDVAY_DOMAIN,
            url = reverse('console_org_home'),
            org_uid = org_mem.organization.org_uid
        )

        # Create message body
        message_body = render_to_response('owlery/owls/emails/org_invitation.html', {
            "org_mem": org_mem,
            "url": url
        }).content

        # Create database entry
        email_msg = EmailMessage.objects.create(
            username = user.username,
            email_id = user.email,

            subject = "Feedvay - {} invitation".format(org_mem.organization.name),
            message = message_body,

            type = EmailMessage.TYPE_ORG_INVTN,
            priority = EmailMessage.PR_HIGH
        )

        # Send email since it is an urgent message
        try:
            email_msg.force_send()
        except:
            pass

        return email_msg

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
    def send_org_invitation(org_mem):
        """
        Sends notifications for organization invitation.

        :param org_mem: Membership instance :class:`clients.models.OrganizationMember`
        :return: Returns :class:`owlery.model.NotificationMessage` instance, None if there are no owners of the brand

        **Authors**: Gagandeep Singh
        """

        url_web = "{url}?c={org_uid}".format(
            url = reverse('console_org_home'),
            org_uid = org_mem.organization.org_uid
        )

        message_body = render_to_response('owlery/owls/notifications/org_invitation.html', {
            "org_mem": org_mem,
        }).content

        # Create entry
        notif_msg = NotificationMessage.objects.create(
            target = NotificationMessage.TARGET_USER,
            transmission = NotificationMessage.TRANSM_MULTICAST,
            type = NotificationMessage.TYPE_ORG_INVTN,
            title = '{} invitation'.format(org_mem.organization.name),
            message = message_body,
            url_web = url_web,
            priority = NotificationMessage.PR_URGENT
        )

        # Create recipient
        NotificationRecipient(
            notif_message = notif_msg,
            registered_user = org_mem.registered_user
        )

        # Send notification
        notif_msg.force_send()

        return notif_msg
