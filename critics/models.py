# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from mongoengine.document import *
from mongoengine.fields import *

from django.contrib.auth.models import User


class Rating(Document):
    """
    Mongodb collection to store user rating on various entities.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    CT_BSP = 'bsp'
    CH_CONTENT_TYPE = (
        (CT_BSP, 'BSP'),
    )

    CH_RATING = (
        (i,i) for i in range(1, 6, 1)
    )

    # --- Fields ---
    content_type = StringField(required=True, choices=CH_CONTENT_TYPE, help_text='Content/Entity on which rating is made.')
    object_id   = StringField(required=True, help_text='Instance ID of the entity which is rated.')

    rating      = IntField(choices=CH_RATING, help_text='Rating on the scale of 1-5.')

    user_id     = IntField(required=True, help_text='Instance ID of User who rated the entity.')
    created_on  = DateTimeField(required=True, default=timezone.now, help_text='Date on which this review was made.')

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    meta = {
        'indexes':[
            ['content_type', 'object_id'],
            'user_id',
            'created_on'
        ]
    }

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete this record.")


class Review(Document):
    """
    Mongodb collection to store user reviews on various entities.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    CT_BSP = 'bsp'
    CH_CONTENT_TYPE = (
        (CT_BSP, 'BSP'),
    )

    # --- Fields ---
    content_type = StringField(required=True, choices=CH_CONTENT_TYPE, help_text='Content/Entity on which review is made.')
    object_id   = StringField(required=True, help_text='Instance ID of the entity which is reviewd.')

    review      = StringField(help_text='User review for the entity')
    # total_likes = IntField(required=True, default=0, help_text='Total likes for this review.')
    # AI

    user_id     = IntField(required=True, help_text='Instance ID of User who rated the entity.')

    hidden      = BooleanField(default=False, help_text='Set true to hide this review.')
    created_on  = DateTimeField(required=True, default=timezone.now, help_text='Date on which this record was created.')
    modified_on = DateTimeField(default=None, help_text='Date on which this record was modified.')

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    meta = {
        'indexes':[
            ['content_type', 'object_id'],
            'user_id',
            'hidden',
            'created_on'
        ]
    }

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """
        if self.pk:
            self.modified_on = timezone.now()

        return super(Review, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete this record. Hide it instead.")

