# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from fcm.utils import FCMMessage

from owlery.models import NotificationMessage
from accounts.models import UserDevice

class FcmPushService:
    """
    Google Firebase Cloud Messaging (FCM) service interface that transforms :class:`owlery.models.NotificationMessage`
    to FCM format suitable for sending.

    **Authors**: Gagandeep Singh
    """

    MAP_PRIORITY = {
        NotificationMessage.PR_LOW : -1,
        NotificationMessage.PR_NORMAL: 0,
        NotificationMessage.PR_HIGH: 1,
        NotificationMessage.PR_URGENT: 2
    }

    def __init__(self, notif):
        """
        Initialization method to transform and load data to be send.

        :param notif: Instance of :class:`owlery.models.NotificationMessage`
        """
        if not isinstance(notif, NotificationMessage):
            raise Exception("'notif' is not instance if NotificationMessage")

        self.notif = notif
        self.priority = FcmPushService.MAP_PRIORITY.get(notif.priority, 0)
        self.is_broadcast = False
        self.collapse_key = notif.type

        # Set transmission
        if notif.transmission == NotificationMessage.TRANSM_MULTICAST:
            # Multicast message; send to all recipient's devices
            self.is_broadcast = False
        elif notif.transmission == NotificationMessage.TRANSM_BROADCAST:
            # Broadcast to the topic or channel
            self.is_broadcast = True
            self.topic = notif.topic_channel
        else:
            raise Exception("Invalid transmission {}".format(notif.transmission))

        # Set data according to the target
        if notif.target == NotificationMessage.TARGET_SYSTEM:
            data = {
                "command": notif.message
            }
        elif notif.target == NotificationMessage.TARGET_USER:
            data = {
                "message": notif.message,
            }

            if notif.title:
                data["title"] = notif.title

            if notif.url_web:
                data["url_web"] = notif.url_web

            if notif.url_mobile:
                data["url_mobile"] = notif.url_mobile
        else:
            raise Exception("Invalid target {}".format(notif.target))

        data['content-available'] = "1"
        data['notId'] = notif.id

        self.data = data

    def send(self):
        """
        Method that actually sends the message. It push it to the service that take cares of all
        delivery challenges.

        **Exceptions**: Throws 'ConnectionError' error if firebase was down.

        :return: (was_send, result) - was_send:(Bool) True if message was send, result: As returned by the service.
        """

        was_send = False
        result = None

        if self.is_broadcast:
            # Broadcast send
            result = FCMMessage().send(
                self.data,
                to = "/topics/{}".format(self.topic),
                collapse_key = self.collapse_key
            )

            was_send = False if result[1].get('failure', 0) else True
        else:
            # Multicast send
            list_user_ids = list(self.notif.notificationrecipient_set.all().values_list('registered_user__user', flat=True))
            list_devices = UserDevice.objects.filter(user__in=list_user_ids)
            result = list_devices.send_message(
                self.data,
                collapse_key = self.collapse_key
            )
            was_send = False if result[1].get('failure', 0) else True

        return (was_send, result)