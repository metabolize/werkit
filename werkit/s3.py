import os
import sys
import typing as t
import uuid
from contextlib import AbstractContextManager, contextmanager


@contextmanager
def temp_file_on_s3(
    local_path: str, bucket: str, key: t.Optional[str] = None, verbose: bool = False
) -> t.Iterator[str]:
    """
    Copy the given path to S3. Delete the object from S3 when the block
    exits.
    """
    import boto3

    def pif(x: str) -> None:
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


@t.overload
def temp_file_on_s3_from_string(
    contents: str,
    bucket: str,
    ret_etag: t.Literal[True],
    key: t.Optional[str] = None,
    extension: t.Optional[str] = None,
    verbose: bool = False,
) -> AbstractContextManager[tuple[str, str]]:
    ...


@t.overload
def temp_file_on_s3_from_string(
    contents: str,
    bucket: str,
    ret_etag: t.Literal[False],
    key: t.Optional[str] = None,
    extension: t.Optional[str] = None,
    verbose: bool = False,
) -> AbstractContextManager[str]:
    ...


@t.overload
def temp_file_on_s3_from_string(
    contents: str,
    bucket: str,
    *,
    ret_etag: bool = False,
    key: t.Optional[str] = None,
    extension: t.Optional[str] = None,
    verbose: bool = False,
) -> AbstractContextManager[str]:
    ...


# @t.overload doesn't work properly with @contextmanager
# https://github.com/python/mypy/issues/14652
@contextmanager  # type: ignore[arg-type]
def temp_file_on_s3_from_string(  # type: ignore[misc]
    contents: str,
    bucket: str,
    ret_etag: bool = False,
    key: t.Optional[str] = None,
    extension: t.Optional[str] = None,
    verbose: bool = False,
) -> t.Union[AbstractContextManager[str], AbstractContextManager[tuple[str, str]]]:
    """
    Write the given contents to S3. Delete the object from S3 when the block
    exits.
    """
    import boto3

    def pif(x: str) -> None:
        if verbose:
            print(x, file=sys.stderr)

    if key is None:
        key = f"{uuid.uuid4().hex}{extension}"

    s3_client = boto3.client("s3")

    file_on_s3 = f"s3://{bucket}/{key}"
    pif(f"Writing to {file_on_s3}")

    response = s3_client.put_object(
        Bucket=bucket, Key=key, Body=contents.encode("utf-8")
    )

    try:
        yield (key, response["ETag"]) if ret_etag else key
    finally:
        pif(f"Removing {file_on_s3}")
        s3_client.delete_object(Bucket=bucket, Key=key)
