# Copyright (C) 2016 Feedvuy (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django_mysql import models as models57

from django.db.models.signals import post_save
from django_mysql.models import JSONField
# from django_extensions.db.fields.json import JSONField
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from hashlib import md5


# ---------- System Exceptions ----------
class ErrorLog(models57.Model):
    """
    Model to store all system errors occurred during runtime as captured by :class:`watchdog.middleware.ErrorLogMiddleware` middleware.

    **Authors**: Gagandeep Singh
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
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """
        if not self.checksum:
            self.checksum = ErrorLog.construct_checksum(self.class_name, self.message, self.traceback)

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Pre-save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()

        # Note: Cannot be in clean() since this might give error in django admin as 'resolved_by' has not been set yet
        if self.is_resolved:
            if self.resolved_by is None or self.resolved_on is None:
                raise ValidationError("'Resolved by' or 'Resolved on' cannot be empty since error has been resolved.")

        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # Override delete method to prevent record deletion.
        raise ValidationError("Denied! You cannot delete error log.")

    @staticmethod
    def construct_checksum(class_name, message, traceback_text=None):
        """
        Constructs a checksum based on class name, error message and traceback text.
        Class name is always used along with traceback text if not null otherwise message.

        **Authors**: Gagandeep Singh
        """

        checksum = md5(class_name)
        message = traceback_text or message
        if isinstance(message, unicode):
            message = message.encode('utf-8', 'replace')
        checksum.update(message)
        return checksum.hexdigest()

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model. This will will called after the record has
        been created or updated.

        **Authors**: Gagandeep Singh
        """

        # Update all ReportedProblems
        # Using 'update'; no save() or signals will be triggered
        instance.reportedproblem_set.all().update(
            status = ReportedProblem.ST_RESOLVED if instance.is_resolved else ReportedProblem.ST_NEW,
            remarks = 'Resolved by ErrorLog:{}'.format(instance.pk) if instance.is_resolved else 'Pending',
            modified_on = instance.resolved_on
        )

post_save.connect(ErrorLog.post_save, sender=ErrorLog)


# ---------- /System Exceptions ----------

# ---------- Suggestions ----------
class Suggestion(models.Model):
    """
    Model to store suggestions made by user for various areas in the system.
    Suggestion is not an error, but rather an area of improvement that user
    feels must be present.

    **Points**:

        - Only logged-in user can make suggestions

    **Authors**: Gagandeep Singh
    """

    PLTFM_MOBILE = 'mobile'
    PLTFM_PORTAL = 'portal'
    CH_PLATFORM = (
        (PLTFM_PORTAL, 'Portal'),
        (PLTFM_MOBILE, 'Mobile')
    )

    ST_NEW = 'new'
    ST_ACCEPTED = 'accepted'
    ST_REJECTED = 'rejected'
    ST_IMPLEMENTED = 'implemented'

    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_REJECTED, 'Rejected'),
        (ST_ACCEPTED, 'Accepted'),
        (ST_IMPLEMENTED, 'Implemented')
    )

    parent      = models.ForeignKey('self', null=True, blank=True, db_index=True, limit_choices_to={'parent':None}, help_text='In case this suggestion is duplicate, link to previously reported suggestion. (For staff use only)')

    platform    = models.CharField(max_length=64, choices=CH_PLATFORM, editable=False, db_index=True, help_text='Platform for which suggestion is made.')
    url         = models.URLField(null=True, blank=True, editable=False, help_text='Page url of the suggestion.')

    title       = models.CharField(max_length=512, editable=False, help_text='Title of the suggestion.')
    description = models.TextField(editable=False, help_text='Detailed description of the suggestion.')

    user        = models.ForeignKey(User, null=True, blank=True, editable=False, db_index=True, help_text='User that made this suggestion.')

    status      = models.CharField(max_length=32, default=ST_NEW, choices=CH_STATUS, help_text='Status of the suggestion. (For staff use only)')
    remarks     = models.TextField(null=True, blank=True, help_text='Remarks/Reason in case of rejection. (For staff use only)')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this suggestion was made.')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def is_duplicate(self):
        # Tells if suggestion is duplicate or not
        return True if self.parent_id else False

    @property
    def children(self):
        # Returns all children (duplicates) for this suggestion
        return self.suggestion_set.all()

    def __unicode__(self):
        return "{} - {}".format(self.id, self.title)

    class Meta:
        ordering = ('-created_on', )

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Parent check
        if self.parent_id is not None:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError('Parent cannot be itself.')
            elif self.parent_id is not None:
                self.status = self.parent.status
                self.remarks = self.parent.remarks

        # Status checks
        if self.status == Suggestion.ST_REJECTED and (self.remarks is None or self.remarks==''):
            raise ValidationError('Please enter remark for rejecting this suggestion.')

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

    def delete(self, using=None, keep_parents=False):
        # Override delete method to prevent record deletion.
        raise ValidationError("Denied! You cannot delete suggestions made by user.")

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model. This will will called after the record has
        been created or updated.

        **Authors**: Gagandeep Singh
        """

        # Update all children
        if instance.parent_id is None:
            # Using 'update'; no save() or signals will be triggered
            Suggestion.objects.filter(parent=instance).update(status=instance.status, remarks=instance.remarks, modified_on=instance.modified_on)

post_save.connect(Suggestion.post_save, sender=Suggestion)

# ---------- Reported Problems ----------
class ReportedProblem(models.Model):
    """
    Model to store errors reported by the users. These do not include errors reported by the system
    however, may be linked to one.

    **Points**:

        - It must not include system problem but only those reported by user.
        - A problems can be linked to :class:`watchdog.models.ErrorLog`.
        - A Problem can be reported by logged in user or public user. Incase of public user, email id is referred.
        - In case of rejecting a problem, remark must be provided.
        - Records inherit from parent first and then from error_log.

    **Authors**: Gagandeep Singh
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

    parent      = models.ForeignKey('self', null=True, blank=True, db_index=True, limit_choices_to={'parent':None}, help_text='Link to previously reported error incase it is duplicate. (For staff use only)')

    platform    = models.CharField(max_length=64, choices=CH_PLATFORM, editable=False, db_index=True, help_text='Platform where error was seen.')
    url         = models.URLField(null=True, blank=True, editable=False, help_text='Page url where error was seen. This can be null if it general error reporting.')

    title       = models.CharField(max_length=512, editable=False, help_text='Title of the problem. This can be pre-filled or filled by user itself')
    description = models.TextField(editable=False, help_text='Detailed description of the problem')

    user        = models.ForeignKey(User, null=True, blank=True, editable=False, db_index=True, help_text='User that reported this problem. This can be empty in case of public user.')
    email_id    = models.EmailField(null=True, blank=True, editable=False, help_text='In case of public user, use email id for reference.')

    error_log   = models.ForeignKey(ErrorLog, null=True, blank=True, db_index=True, help_text='Reference to error log for debugger convenience. (For staff use only)')

    status      = models.CharField(max_length=32, choices=CH_STATUS, default=ST_NEW, help_text='Status of the problem')
    remarks     = models.TextField(null=True, blank=True, help_text='Remarks/Reason in case of rejection. (For staff use only)')

    created_on  = models.DateTimeField(auto_now_add=True, editable=False, db_index=True, help_text='Date on which this problem was reported')
    modified_on = models.DateTimeField(null=True, blank=True, editable=False, help_text='Date on which this record was modified.')

    @property
    def is_duplicate(self):
        # Tells if problem is duplicated based on the fact that 'parent' field is linked.
        return True if self.parent_id else False

    @property
    def children(self):
        # Returns all children (duplicates) for this problem
        return self.reportedproblem_set.all()

    class Meta:
        ordering = ('-created_on',)

    def __unicode__(self):
        return "{} - {}".format(self.pk, self.title)

    def clean(self):
        """
        Method to clean & validate data fields.

        **Authors**: Gagandeep Singh
        """

        # Parent check
        if self.parent is not None:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError('Parent cannot be itself.')
            else:
                self.status = self.parent.status
                self.remarks = self.parent.remarks
                self.error_log_id = self.parent.error_log_id
        else:
            if self.error_log_id:
                self.status = ReportedProblem.ST_RESOLVED if self.error_log.is_resolved else ReportedProblem.ST_NEW

        # User & email check
        if self.user:
            self.email_id = self.user.email
        else:
            if self.email_id is None:
                raise ValidationError('Email id required since user is not specified.')

        # Status checks
        if self.status == ReportedProblem.ST_REJECTED and (self.remarks is None or self.remarks==''):
            raise ValidationError('Please enter remark for rejecting this problem.')

        if self.pk:
            # Update modified date
            self.modified_on = timezone.now()

        super(self.__class__, self).clean()

    def save(self, *args, **kwargs):
        """
        Post save trigger for this model. This will will called after the record has
        been created or updated.

        **Authors**: Gagandeep Singh
        """
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


    def delete(self, using=None, keep_parents=False):
        # Override delete method to prevent record deletion.
        raise ValidationError("Denied! You cannot delete reported by the users.")

    @classmethod
    def post_save(cls, sender, instance, **kwargs):
        """
        Post save trigger for this model. This will will called after the record has
        been created or updated.

        **Authors**: Gagandeep Singh
        """

        # Update all children
        if instance.parent_id is None:
            # Using 'update'; no save() or signals will be triggered
            ReportedProblem.objects.filter(parent=instance).update(
                error_log = instance.error_log,
                status = instance.status,
                remarks = instance.remarks,
                modified_on = instance.modified_on
            )

post_save.connect(ReportedProblem.post_save, sender=ReportedProblem)

# ---------- /Reported Problems ----------
