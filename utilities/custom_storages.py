# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

class MediaStorage(S3BotoStorage):
        location = settings.MEDIAFILES_LOCATION

