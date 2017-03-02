# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from django.utils import timezone
import uuid

MAPPING_MONGO_FLD_PYTHON = {
    "StringField": str,
    "ObjectIdField": str,
    "URLField": str,
    "EmailField": str,
    "FileField": str,
    "IntField": int,
    "SequenceField": int,
    "LongField": long,
    "FloatField": float,
    "DecimalField": float,
    "ListField": list,
    "EmbeddedDocumentListField": list,
    "SortedListField": list,
    "DictField": dict,
    "EmbeddedDocumentField": dict,
    "GenericEmbeddedDocumentField": dict,
    "BooleanField": bool,
    "DateTimeField": timezone.datetime,
    "ComplexDateTimeField": timezone.datetime,
    "UUIDField": uuid.uuid4,
    "GeoPointField": list
}