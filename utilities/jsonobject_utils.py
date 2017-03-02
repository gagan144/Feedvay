# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from jsonobject.properties import *

from django.utils import timezone
from datetime import date, time

MAPPING_JSNOBJ_FLD_PYTHON = {
    "StringProperty": str,
    "IntegerProperty": int,
    "FloatProperty": float,
    "DecimalProperty": float,
    "BooleanProperty": bool,
    "DateProperty": date,
    "DateTimeProperty": datetime,
    "TimeProperty": time,
    "ListProperty": list,
    "SetProperty": set,
    "ObjectProperty": dict,
    "DictProperty": dict
}