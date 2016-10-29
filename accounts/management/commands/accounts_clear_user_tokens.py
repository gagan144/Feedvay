# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import UserToken

class Command(BaseCommand):
    """
    Django management command to delete all expired user tokens from model
    :class:`accounts.models.UserToken`.
    """
    help = "Command to delete all expired 'UserToken'."
    requires_system_checks = True
    can_import_settings = True

    # ----- Main executor -----
    def handle(self, *args, **options):
        # Import django settings
        from django.conf import settings

        now = timezone.now()

        # Delete all 'UserToken' that are expired as of now
        result = UserToken.objects.filter(expire_on__lt=now).delete()

        count = result[0]
        self.stdout.write(self.style.SUCCESS('{} expired user tokens successfully deleted.'.format(count)))
