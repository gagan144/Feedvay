# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
import traceback
import socket
import warnings
import json
from django.utils import timezone

from watchdog.models import ErrorLog


WATCHDOG_ERRORLOG_ENABLED = getattr(settings, 'WATCHDOG_ERRORLOG_ENABLED', True)

class ErrorLogMiddleware(MiddlewareMixin):
    """
    Middleware to capture exceptions occurred at runtime for a request and
    log it into database if error logging is enabled through ``settings.WATCHDOG_ERRORLOG_ENABLED``

    **Authors**: Gagandeep Singh
    """
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied) or isinstance(exception, Http404):
            return
        elif WATCHDOG_ERRORLOG_ENABLED:
            server_name = socket.gethostname()
            class_name = exception.__class__.__name__
            message = getattr(exception, 'message', '')
            traceback_text = traceback.format_exc()

            checksum = ErrorLog.construct_checksum(class_name, message, traceback_text)
            user = request.user
            data = request.POST if request.method.lower() == 'post' else {}

            try:
                error_log, is_new = ErrorLog.objects.update_or_create(
                    server_name = server_name,
                    class_name = class_name,
                    checksum = checksum,

                    defaults = dict(
                        url = request.build_absolute_uri(),
                        message = getattr(exception, 'message', ''),
                        traceback = traceback_text,
                        data = data,
                        last_seen_by = None if user.is_anonymous() else user
                    )
                )

                if not is_new:
                    error_log.times_seen += 1
                    error_log.last_seen_on = timezone.now()
                    error_log.is_resolved = False
                    error_log.save()
            except Exception, exc:
                pass
