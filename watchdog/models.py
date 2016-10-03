# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# from django_mysql.models import JSONField
from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from hashlib import md5


# ---------- System Exceptions ----------
class ErrorLog(models.Model):
    """
    Model to store all exceptions occurred during runtime as captured by ErrorLogMiddleware middleware.
    """

    server_name     = models.CharField(max_length=128, db_index=True, help_text='IP address of the server on which exception occured.')
    url             = models.URLField(null=True, blank=True, db_index=True, help_text='Url at which this exception occured.')

    class_name      = models.CharField(max_length=128, db_index=True, help_text='Class of Exception.')
    message         = models.TextField(help_text='Message of the exception.')
    traceback       = models.TextField(blank=True, null=True, help_text='Complete traceback of the exception occured.')
    checksum        = models.CharField(max_length=32, db_index=True, editable=False)
    data            = JSONField(blank=True, null=True)

    times_seen      = models.PositiveIntegerField(default=1, help_text='No of times this error has been seen.')
    first_seen_on   = models.DateTimeField(auto_now_add=True, db_index=True, help_text='Date on which this error was first seen.')
    last_seen_on    = models.DateTimeField(auto_now_add=True, db_index=True, help_text='Date on which this error was last seen. (Can be equal to first seen)')
    last_seen_by    = models.ForeignKey(User, related_name='last_seen_by', null=True, blank=True, help_text='Last user that saw this error.')

    is_resolved     = models.BooleanField(default=False, db_index=True, help_text='If checked, error has been resolved.')
    resolved_by     = models.ForeignKey(User, null=True, blank=True, db_index=True, help_text='Last user who resolved this problem')
    resolved_on     = models.DateTimeField(null=True, blank=True, db_index=True, help_text='Date on which this problem was last resolved.')

    class Meta:
        unique_together = ('server_name', 'class_name', 'checksum')
        ordering = ('-last_seen_on',)

    def __unicode__(self):
        return str(self.id)

    def shortened_url(self):
        if not self.url:
            return _('no data')
        url = self.url
        if len(url) > 60:
            url = url[:60] + '...'
        return url
    shortened_url.allow_tags = True
    shortened_url.short_description = _('url')

    def full_url(self):
        return self.data.get('url') or self.url
    full_url.short_description = _('url')

    def save(self, *args, **kwargs):
        if self.is_resolved:
            if self.resolved_by is None or self.resolved_on is None:
                raise Exception("'Resolved By' or 'Resolved On' cannot be empty since error has been resolved.")

        if not self.checksum:
            self.checksum = ErrorLog.construct_checksum(self.class_name, self.message, self.traceback)

        super(ErrorLog, self).save(*args, **kwargs)

    @staticmethod
    def construct_checksum(class_name, message, traceback_text=None):
        """
        Constructs a checksum based on class name, error message and traceback text.
        Class name is always used along with traceback text if not null otherwise message.
        """
        checksum = md5(class_name)
        message = traceback_text or message
        if isinstance(message, unicode):
            message = message.encode('utf-8', 'replace')
        checksum.update(message)
        return checksum.hexdigest()


# ---------- /System Exceptions ----------