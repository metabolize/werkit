import os
import sys
import uuid
from contextlib import contextmanager


@contextmanager
def temp_file_on_s3(local_path, bucket, key=None, verbose=False):
    """
    Copy the given path to S3. Delete the file from S3 when the block exits.
    """
    import boto3

    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    if key is None:
        filename, extension = os.path.splitext(os.path.basename(local_path))
        key = f"{filename}_{uuid.uuid4().hex}{extension}"

    s3_client = boto3.client("s3")

    file_on_s3 = f"s3://{bucket}/{key}"
    pif(f"Uploading {local_path} to {file_on_s3}")
    s3_client.upload_file(Filename=local_path, Bucket=bucket, Key=key)

    try:
        yield key
    finally:
        pif(f"Removing {file_on_s3}")
        s3_client.delete_object(Bucket=bucket, Key=key)
