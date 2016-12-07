# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from __future__ import unicode_literals

from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from mongoengine.document import *
from mongoengine.fields import *
from mongoengine.connection import connect
from mongoengine import signals as mongo_signals
from bson.objectid import ObjectId
from bson import json_util

from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from django.template.defaultfilters import slugify


class Language(models.Model):
    """
    Model to define various languages available in the form.
    English is included by default, so do not make entry for english.

    Table collation: utf8_*
        ALTER TABLE languages_language CONVERT TO CHARACTER SET utf8 COLLATE utf8_unicode_ci;

    **Authors**: Gagandeep Singh
    """

    # Enums for default language 'English'. Be careful will changing it.
    DEFAULT_LANGUAGE = 'English'
    DEFAULT_LANGUAGE_CODE = 'eng'
    DEFAULT_LANGUAGE_CODES = ['en', 'eng']

    # Model fields
    help_text_code = 'Code of the language as per ISO 639-1,2. In case of language is not in the list, use unique code.' \
                     '<br/>Reference: <a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" target="_balnk">https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes</a>'

    code        = models.CharField(max_length=20, unique=True, db_index=True, help_text=help_text_code)
    name        = models.CharField(max_length=255, unique=True, db_index=True, help_text="Name of the language.")
    name_native = models.CharField(max_length=255, help_text="Name of the language in its native form.")
    description = models.TextField(null=True, blank=True, help_text="Some description about this language.")
    active      = models.BooleanField(default=True, help_text="Active/Deactive language. This will not affect any currently using language.")

    created_on  = CreationDateTimeField(db_index=True, help_text='Date on which this language was created.')
    updated_on  = ModificationDateTimeField(auto_now=False, null=True, blank=True, db_index=True, help_text='Date on which this language was last updated.')

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        Clean and validation method.

        **Authors**: Gagandeep Singh
        """
        if self.code in Language.DEFAULT_LANGUAGE_CODES or self.name == Language.DEFAULT_LANGUAGE:
            raise ValidationError("English is already included.")

    def save(self, *args, **kwargs):
        """
        Pre save method for this model.

        **Authors**: Gagandeep Singh
        """
        self.clean()

        if self.id:
            self.updated_on = datetime.now()
        return super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise Exception("You cannot delete this language. Mark inactive instead.")

class Translation(Document):
    """
    Model to define various sentences and their translation to different kind of languages as define in
    :class:`languages.models.Language` model.

    .. note::
        When adding new field, update the following code area as well:
        1. languages.view.save_translation()

    **Authors**: Gagandeep Singh
    """

    unique_id       = StringField(required=True, unique=True, help_text="User defined unique id of the translation. By default, value is mongo id of this record.")
    is_paragraph    = BooleanField(default=False, help_text="If true, it means translation text are big paragraphs.")
    sentence        = StringField(required=True, help_text="Default english sentence. Code: eng")
    translations    = DictField(help_text="Dictionary of translations for various languages other than english.")
    list_language_codes  = ListField(help_text="List of all language codes whose translation of this senetence is provided in translations.")

    tags            = ListField(StringField(), default=None, help_text="List of tags names to to tag this tranlsation for easy search.")
    is_public       = BooleanField(default=False, required=True, help_text="If true, this translation is publicly available to be used anywhere.")
    always_include_in_form = BooleanField(default=False, help_text="If true, this transaltion will be included to forms translations by default.")

    created_on      = DateTimeField(required=True, default=datetime.now, help_text="Date on which this translation was created.")
    updated_on      = DateTimeField(help_text="Date on which this translation was last updated.")

    meta = {
        "indexes":[
            "unique_id",
            "is_paragraph",
            "$sentence",    # Text index
            "list_language_codes",
            "tags",
            "is_public",
            "always_include_in_form",
            "created_on"
        ]
    }

    def __unicode__(self):
        return str(self.pk)

    def to_js_json(self):
        data = self.to_mongo()
        data["id"] = str(self.pk)
        del data["_id"]
        return json_util.dumps(data)

    def save(self, complete_save=True, *args, **kwargs):
        """
        Pre save method for this model.

        **Authors**: Gagandeep Singh
        """
        # Set unique_id if None
        if not self.unique_id:
            # NOTE: Here pk is None for new record which is updated in post_save using raw query
            self.unique_id = str(self.pk)
        self.unique_id = slugify(self.unique_id)

        # Update 'list_language_codes'
        self.list_language_codes = []
        for key in self.translations:
            lang = Language.objects.get(code=key)
            self.list_language_codes.append(key)

        if self.pk:
            self.updated_on = datetime.now()

        return super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """
        Routine to execute after the translation has been saved.

        **Authors**: Gagandeep Singh
        """
        id = str(document.pk)
        if document.unique_id == 'none':
            Translation._get_collection().find_one_and_update(
                filter = {'_id': ObjectId(id)},
                update = {'$set': {'unique_id': id}}
            )
mongo_signals.post_save.connect(Translation.post_save, sender=Translation)