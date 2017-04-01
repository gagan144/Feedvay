# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import ujson

from mongoengine.document import *
from mongoengine.fields import *

from clients.models import Organization

class ImportRecord(Document):
    """
    Mongo model to store data of any schema. This model act as a buffer storage
    for bulk uploads where records can be stored and later picked-up by process
    that uses them.

    Each record belongs to a context which is associated with a process. Each process
    looks for records of its context and processes it.

    After processing, the record is removed from this collection. This is the responsibility of the
    process.

    .. warning::
        The schema of ``identifiers`` and ``data`` can be anything. Please be careful setting these
        fields and make sure process that processes them can understand it.

    **Authors**: Gagandeep Singh
    """

    CNTX_BSP = 'bsp'
    CNTX_GEO_LOC = 'geo_location'
    CH_CONTEXT = (
        (CNTX_BSP, 'BSP'),
        (CNTX_GEO_LOC, 'GeoLocation'),
    )

    ST_NEW = 'new'
    ST_PROCESSING = 'processing'
    ST_ERROR = 'error'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_PROCESSING, 'Processing'),
        (ST_ERROR, 'Error'),
    )

    organization_id = IntField(help_text="(Optional) Organization to which this record belongs to.")
    batch_id    = StringField(required=True, help_text='Batch id of bulk upload for this record.')

    context     = StringField(required=True, choices=CH_CONTEXT, help_text="Context of the record.")
    filename    = StringField(help_text="Uploaded file name that created this record.")
    identifiers = DictField(help_text="Identifiers that describe this data record.")
    data        = StringField(required=True, help_text="JSON dict string containing actual data for the record. This is string because mongo does not allow dot in keys.")

    status      = StringField(required=True, default=ST_NEW, choices=CH_STATUS, help_text="Status of this record.")
    error_message = StringField(help_text="Error details in case processing encountered any error.")

    created_by  = IntField(help_text="Instance id of user :class:`django.contrib.auth.models.User` who created this record.")
    created_on  = DateTimeField(default=timezone.now, required=True, confidential=True, help_text='Date on which this record was created in the database.')
    modified_on = DateTimeField(default=None, confidential=True, help_text='Date on which this record was modified.')

    @property
    def data_json(self):
        return ujson.loads(self.data)

    @property
    def organization(self):
        return Organization.objects.get(id=self.organization_id)

    meta = {
        'ordering': ['context', 'batch_id'],
        'indexes':[
            { 'fields':['organization_id'], 'cls':False, 'sparse': True },
            'batch_id',
            'context',
            'status',
            'created_on',
        ]
    }


    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for this model.

        **Authors**: Gagandeep Singh
        """
        # Check status
        if self.status == ImportRecord.ST_ERROR and self.error_message in ["", None]:
            raise ValidationError("Please specify error message.")

        # Check data json
        try:
            d = self.data_json
        except ValueError as ex:
            raise ValidationError(ex.message)

        if self.pk:
            self.modified_on = timezone.now()

        return super(ImportRecord, self).save(*args, **kwargs)


class ResponseQueue(Document):
    """
    Mongodb collection to store all submitted responses for all types of forms. All responses received
    are queued in this collection immediately without any pre-processing. These are then later picked-up by a
    process that processes them and migrate into corresponding models as per the ``context``.

    **Points**:

        - ``status`` state chart is custom implemented similar to 'django-fsm'. However, this is not
          error-proof since ``status`` field is not PROTECTED. Please change state carefully and always
          use transition methods only.

    .. note::
        Responses which are successfully processed are **removed** from this collection.

    .. warning::
        **DO NOT** update ``status`` directly. Always use transition methods. Also, make sure
        you call save() method are calling transition method.

    **Authors**: Gagandeep Singh
    """
    # --- ENUMS ---
    CT_BSP_FEEDBACK = 'bsp_feedback'
    CH_CONTEXT = (
        (CT_BSP_FEEDBACK, 'BSP Feedback')
    )

    ST_NEW = 'new'
    ST_PROCESSING = 'processing'
    ST_FAILED = 'failed'
    CH_STATUS = (
        (ST_NEW, 'New'),
        (ST_PROCESSING, 'Processing'),
        (ST_FAILED, 'Failed')
    )

    context     = StringField(required=True, choices=CH_CONTEXT, help_text='Context of the responses. This defines how the response must be processed.')
    data        = StringField(required=True, help_text='Response data. This is mostly JSON string.')

    status      = StringField(required=True, default=ST_NEW, choices=CH_STATUS, help_text='Status of the record.')
    error_title = StringField(help_text='Error message if processing failed.')
    error_traceback = StringField(help_text='Error traceback used for debugging.')

    created_on  = DateTimeField(required=True, default=timezone.now, help_text='Datetime on which this record was created or was received at the server.')
    modified_on = DateTimeField(default=None, help_text='Date on which this record was modified.')

    meta = {
        'ordering': ['created_on'],
        'indexes': [
            'context',
            'status',
            'created_on',
            'modified_on'
        ]
    }

    def __unicode__(self):
        return "{} - {}".format(self.context, self.pk)

    # --- Transitions ---
    def trans_process(self):
        """
        Transition method to change state from NEW to PROCESSING.

        **Authors**: Gagandeep Singh
        """
        if self.status not in [ResponseQueue.ST_NEW, ResponseQueue.ST_FAILED]:
            raise ValidationError("Invalid Transition")

        self.status = ResponseQueue.ST_PROCESSING

    def trans_failed(self, error_title, error_traceback):
        """
        Transition method to change state from PROCESSING to FAILED.

        **Authors**: Gagandeep Singh
        """
        if self.status != ResponseQueue.ST_PROCESSING:
            raise ValidationError("Invalid Transition")

        self.status = ResponseQueue.ST_FAILED
        self.error_title = error_title
        self.error_traceback = error_traceback

    # --- /Transitions ---

    def save(self, *args, **kwargs):
        """
        Save method for this model.

        **Authors**: Gagandeep Singh
        """
        if self.status == ResponseQueue.ST_FAILED:
            if self.error_title is None or self.error_traceback is None:
                raise ValidationError("Error title and traceback are required when status is failed.")

        if self.pk:
            self.modified_on = timezone.now()

        return super(ResponseQueue, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        """
        Pre-Delete method for this model.

        **Authors**: Gagandeep Singh
        """
        if self.status == ResponseQueue.ST_NEW:
            raise ValidationError("You cannot delete response with status 'new'")

        return super(ResponseQueue, self).delete(write_concern)

