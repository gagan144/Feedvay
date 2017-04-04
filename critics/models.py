# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine import signals as mongo_signals
from bson.objectid import ObjectId

from django.contrib.auth.models import User

class Entities:
    COMMENT = 'comment'
    BSP = 'bsp'

    @staticmethod
    def get_model(entity):
        if entity == Entities.COMMENT:
            return Comment
        elif entity == Entities.BSP:
            from market.models import BusinessServicePoint
            return BusinessServicePoint


class Like(Document):
    """
    Mongodb collection to store user likes on various entities.

    Likes can be deleted since one can undo his like.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---

    CH_CONTENT_TYPE = (
        (Entities.COMMENT, 'Comment')
    )

    content_type = StringField(required=True, choices=CH_CONTENT_TYPE, help_text='Content/Entity on which like is made.')
    object_id   = StringField(required=True, help_text='Instance ID of the entity which is liked.')

    user_id     = IntField(required=True, help_text='Instance ID of User who rated the entity.')
    dated       = DateTimeField(required=True, help_text='Date on which this review was made.')

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    meta = {
        'indexes':[
            { 'fields':['content_type', 'object_id', 'user_id'], 'cls':False, 'unique': True },
            'user_id',
            '-dated'
        ]
    }

    def __unicode__(self):
        return "{}-{} {}".format(self.content_type, self.object_id, self.user_id)

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for this record.

        **Authors**: Gagandeep Singh
        """
        if self.pk is not None:
            raise ValidationError("You cannot update Like record.")

        return super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """
        Routine to execute after the like has been saved.

        **Authors**: Gagandeep Singh
        """
        # Only if like is newly created
        if kwargs.get('created', False):
            if document.content_type == Entities.COMMENT:
                entity = Entities.get_model(document.content_type)

                entity._get_collection().find_one_and_update(
                    filter = {'_id': ObjectId(document.object_id)},
                    update = {
                        '$inc':{
                            'total_likes': 1
                        },
                        '$set': {
                            'modified_on': timezone.now()
                        },
                    }
                )

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        """
        Routine to execute after the like has been deleted.

        **Authors**: Gagandeep Singh
        """
        if document.content_type == Entities.COMMENT:
            # Comment
            entity = Entities.get_model(document.content_type)

            entity._get_collection().find_one_and_update(
                filter = {'_id': ObjectId(document.object_id)},
                update = {
                    '$inc':{
                        'total_likes': -1
                    },
                    # Not modifying 'modified_on' field here
                    # '$set': {
                    #     'modified_on': timezone.now()
                    # },
                }
            )

mongo_signals.post_save.connect(Like.post_save, sender=Like)
mongo_signals.post_delete.connect(Like.post_delete, sender=Like)

class Rating(Document):
    """
    Mongodb collection to store user rating on various entities.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    CH_CONTENT_TYPE = (
        (Entities.BSP, 'BSP'),
    )

    CH_RATING = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    # --- Fields ---
    organization_id = IntField(help_text="InstanceID of the organization.")
    content_type = StringField(required=True, choices=CH_CONTENT_TYPE, help_text='Content/Entity on which rating is made.')
    object_id   = StringField(required=True, help_text='Instance ID of the entity which is rated.')

    rating      = IntField(choices=CH_RATING, help_text='Rating on the scale of 1-5.')

    batch_id    = StringField(sparse=True, unique=True, help_text="BatchID to glue all other related entities. For example a batchId may glue feedback response, comment, rating together since they were answer together. ")

    user_id     = IntField(required=True, help_text='Instance ID of User who rated the entity.')
    dated       = DateTimeField(required=True, help_text='Date on which this review was made.')

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    def __unicode__(self):
        return "{}-{} by {}".format(self.content_type, self.object_id, self.user_id)

    meta = {
        'indexes':[
            { 'fields':['organization_id'], 'cls':False, 'sparse': True },
            ['content_type', 'object_id'],
            { 'fields':['batch_id'], 'cls':False, 'sparse': True, 'unique': True },
            'user_id',
            '-dated'
        ]
    }

    def save(self, *args, **kwargs):
        """
        Save method for this model.

        **Authors**: Gagandeep Singh
        """
        if self.pk is not None:
            raise ValidationError("You cannot update rating record.")

        return super(Rating, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """
        Post-save method for this model.

        **Authors**: Gagandeep Singh
        """
        # Only if like is newly created
        if kwargs.get('created', False):
            if document.content_type == Entities.BSP:
                # Business or Service Point
                entity_model = Entities.get_model(document.content_type)

                # Get average rating
                result_aggr = Rating._get_collection().aggregate([
                    {
                        "$match": {
                            "content_type": Entities.BSP,
                            "object_id": document.object_id
                        }
                    },
                    {
                        "$group": {
                            "_id": None, "avg_rating" : { "$avg": "$rating" }
                        }
                    }
                ])

                avg_rating = 0
                for row in result_aggr:
                    avg_rating = row["avg_rating"]
                    break

                entity_model._get_collection().find_one_and_update(
                    filter = {'_id': ObjectId(document.object_id)},
                    update = {
                        '$set':{
                            'avg_rating': avg_rating
                        }
                        # Not modifying 'modified_on' field here
                    }
                )


    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete this record.")
mongo_signals.post_save.connect(Rating.post_save, sender=Rating)


class Comment(Document):
    """
    Mongodb collection to store user comments on various entities.

    For capturing reply for comments, set set content_type as 'comment'.

    **Specifications for ``ai`` field**:

            .. code-block:: json

                {
                    "<algo_key>":{
                        "pending": true,
                        "result": {

                        }
                    }
                }


            **Points**:

                - The structure is created during comment creation after analyzing if AI has to be applied. If so,
                  ``ai_pending`` is set as ``True`` indicating that AI is yet to be applied.
                - All process looks for its ``algo_key`` to check if what algos has to be applied.
                - If ``algo_key.pending`` is true, it means that algo is yet to be processed, so process it.
                  Otherwise, if false, it means comment must have already been processed for that algo.
                - Results are store in ``algo_key.results`` mostly in form of json. Structure varies as per the algorithm result.

    **Authors**: Gagandeep Singh
    """
    # --- Enums ---
    CH_CONTENT_TYPE = (
        (Entities.BSP, 'BSP'),
        (Entities.COMMENT, 'Comment')
    )

    # --- Fields ---
    organization_id = IntField(help_text="InstanceID of the organization.")
    content_type = StringField(required=True, choices=CH_CONTENT_TYPE, help_text='Content/Entity on which review is made.')
    object_id   = StringField(required=True, help_text='Instance ID of the entity which is reviewd.')

    text        = StringField(help_text='User comment for the entity')
    total_likes = IntField(required=True, default=0, help_text='Total likes for this review.')

    ai_pending  = BooleanField(help_text='It true, it means ai has to be applied on comment text.')
    ai          = DictField(default=None, required=False, help_text='AI instructions and results.')

    batch_id    = StringField(sparse=True, unique=True, help_text="BatchID to glue all other related entities. For example a batchId may glue feedback response, comment, rating together since they were answer together. ")

    user_id     = IntField(required=True, help_text='Instance ID of User who rated the entity.')

    hidden      = BooleanField(default=False, help_text='Set true to hide this review.')
    dated       = DateTimeField(required=True, help_text='Date on which this record was created.')
    modified_on = DateTimeField(default=None, help_text='Date on which this record was modified.')

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    def __unicode__(self):
        return "{}-{} by {}".format(self.content_type, self.object_id, self.user_id)

    meta = {
        'indexes':[
            { 'fields':['organization_id'], 'cls':False, 'sparse': True },
            ['content_type', 'object_id'],
            { 'fields':['ai_pending'], 'cls':False, 'sparse': True },
            { 'fields':['batch_id'], 'cls':False, 'sparse': True, 'unique': True },
            'user_id',
            'hidden',
            '-dated'
        ]
    }

    def save(self, update_attr=True, *args, **kwargs):
        """
        Save method for a response.

        **Authors**: Gagandeep Singh
        """
        if self.pk:
            self.modified_on = timezone.now()

        return super(Comment, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        """
        Pre-delete method. (Not allowed)

        **Authors**: Gagandeep Singh
        """
        raise ValidationError("You cannot delete this record. Hide it instead.")

