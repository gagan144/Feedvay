# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf import settings
import boto
from boto.s3.key import Key
import mimetypes

def upload_to_s3(file_obj, filename, path, content_type=None):
    """
    Method to upload a file to s3 and return a link.
    This method automatically tries to guess  of the file using filename if content_type is not passed.

    :param file_obj: File object (this must not be closed)
    :param path: Path where file is to be uploaded (this does not include filename)
    :param content_type: Content-type of the file.
    :return: AWS file url
    """
    # Connect to the bucket
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    key_path = "{}/{}".format(path, filename)

    k = Key(bucket)
    k.key = key_path

    if content_type is None:
        # content_type passed; Guess the type
        content_type = mimetypes.guess_type(filename)[0]

    # Now set type only if is not None
    if content_type:
        k.content_type = content_type

    k.set_contents_from_string(file_obj.read())
    k.make_public()

    return "https://{}/{}".format(settings.AWS_S3_CUSTOM_DOMAIN, key_path)
