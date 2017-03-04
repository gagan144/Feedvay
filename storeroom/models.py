# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from mongoengine.document import *
from mongoengine.fields import *

class Record(Document):
    """
    Mongo model to store data of any schema. This model act as a buffer storage
    for bulk uploads where records can be stored and later picked-up by process
    that uses them.

    Each record belongs to a context which is associated with a process. Each process
    looks for records of its context and processes it.

    After processing, the record is removed from this collection. This is the responsibility of the
    process.

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

    context     = StringField(required=True, choices=CH_CONTEXT, help_text="Context of the record.")
    data        = DictField(required=True, help_text="Key-value based actual data of the record.")

    status      = StringField(required=True, default=ST_NEW, choices=CH_STATUS, help_text="Status of this record.")
    error_message = StringField(help_text="Error details in case processing encountered any error.")

    created_on  = DateTimeField(default=timezone.now, required=True, confidential=True, help_text='Date on which this record was created in the database.')
    modified_on = DateTimeField(default=None, confidential=True, help_text='Date on which this record was modified.')

    meta = {
        'ordering': ['context', 'created_on'],
        'indexes':[
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
        if self.status == Record.ST_ERROR and self.error_message in ["", None]:
            raise ValidationError("Please specify error message.")

        if self.pk:
            self.modified_on = timezone.now()

        return super(Record, self).save(*args, **kwargs)


