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
    CH_CONTEXT = (
        (CNTX_BSP, 'BSP'),
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
    identifiers = DictField(required=True, help_text="Identifiers that describe this data record.")
    data        = StringField(required=True, help_text="JSON dict string containing actual data for the record. This is string because mongo does not allow dot in keys.")

    status      = StringField(required=True, default=ST_NEW, choices=CH_STATUS, help_text="Status of this record.")
    error_message = StringField(help_text="Error details in case processing encountered any error.")

    created_by  = IntField(required=True, help_text="Instance id of user :class:`django.contrib.auth.models.User` who created this record.")
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


