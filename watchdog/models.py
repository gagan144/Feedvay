# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# from django_mysql.models import JSONField
from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from hashlib import md5


# ---------- System Exceptions ----------
class ErrorLog(models.Model):
    """
    Model to store all system errors occurred during runtime as captured by ErrorLogMiddleware middleware.
    """

    server_name     = models.CharField(max_length=128, db_index=True, help_text='IP address of the server on which exception occured.')
    url             = models.URLField(null=True, blank=True, db_index=True, help_text='Url at which this exception occured.')

    class_name      = models.CharField(max_length=128, db_index=True, help_text='Class of the Exception.')
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

    def clean(self):
        if self.is_resolved:
            if self.resolved_by is None or self.resolved_on is None:
                raise ValidationError("'Resolved by' or 'Resolved on' cannot be empty since error has been resolved.")

        if not self.checksum:
            self.checksum = ErrorLog.construct_checksum(self.class_name, self.message, self.traceback)

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

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

# ---------- Reported Problems ----------
class ReportedProblem(models.Model):
    """
    Model to store all errors reported by the users. These do not include errors reported by the system however,
    may be linked to one.

    Points
    ------

        - It must not include system problem but only those reported by user
        - A problems can be linked to :model:`watchdog.ErrorLog`.
        - A Problem can be reported by logged in user or public user. Incase of public user, email id is referred.
        - In case of rejecting problem, remark must be provided.
    """

    PLTFM_MOBILE = 'mobile'
    PLTFM_PORTAL = 'portal'
    CH_PLATFORM = (
        (PLTFM_PORTAL, 'Portal'),
        (PLTFM_MOBILE, 'Mobile')
    )

    ST_NEW = 'new'
    ST_RESOLVED = 'resolved'
    ST_REJECTED = 'rejected'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_RESOLVED, 'Resolved'),
        (ST_REJECTED, 'Rejected')
    )

    parent      = models.ForeignKey('self', null=True, blank=True, db_index=True, help_text='Link to previously reported error incase it is duplicate. (For staff use only)', limit_choices_to={'parent':None})

    platform    = models.CharField(max_length=64, choices=CH_PLATFORM, editable=False, db_index=True, help_text='Platform where error was seen.')
    url         = models.URLField(null=True, blank=True, editable=False, help_text='Page url where error was seen. This can be null if it general error reporting.')

    title       = models.CharField(max_length=512, editable=False, help_text='Title of the problem. This can be pre-filled or filled by user itself')
    description = models.TextField(editable=False, help_text='Detailed description of the problem')

    user        = models.ForeignKey(User, null=True, blank=True, editable=False, db_index=True, help_text='User that reported this problem. This can be empty in case of public user.')
    email_id    = models.EmailField(null=True, blank=True, editable=False, help_text='In case of public user, use email id for reference.')

    error_log   = models.ForeignKey(ErrorLog, null=True, blank=True, db_index=True, help_text='Reference to error log for debugger convenience. (For staff use only)')

    status      = models.CharField(max_length=32, default=ST_NEW, help_text='Status of the problem')
    remarks     = models.TextField(null=True, blank=True, help_text='Remarks/Reason in case of rejection. (For staff use only)')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this problem was reported')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    class Meta:
        ordering = ('-created_on',)

    def is_duplicate(self):
        # Tells if problem is duplicated based on the fact that 'parent' field is linked.
        return True if self.parent else False

    def clean(self):
        # Reporter checks
        if self.user:
            self.email_id = self.user.email
        else:
            if self.email_id is None:
                raise ValidationError('Email id required since user is not specified.')

        # Status checks
        if self.status == ReportedProblem.ST_REJECTED and (self.remarks is None or self.remarks==''):
            raise ValidationError('Please enter remark for rejecting this problem.')

        if self.pk:
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

# ---------- /Reported Problems ----------