import os
import sys
from contextlib import contextmanager
import boto3

DEFAULT_RUNTIME = "python3.7"


def needs_s3_upload(path_to_zipfile):
    return os.path.getsize(path_to_zipfile) > 50 * 2 ** 20


def random_string(length):
    import random
    import string

    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


@contextmanager
def temp_file_on_s3(local_path, bucket, key, verbose=True):
    """
    Copy the given path to S3. Delete the file from S3 when the block exits.
    """

    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    s3_client = boto3.client("s3")

    file_on_s3 = f"s3://{bucket}/{key}"
    pif(f"Uploading {local_path} to {file_on_s3}")
    s3_client.upload_file(Filename=local_path, Bucket=bucket, Key=key)

    try:
        yield
    finally:
        pif(f"Removing {file_on_s3}")
        s3_client.delete_object(Bucket=bucket, Key=key)


def perform_create(
    path_to_zipfile,
    handler,
    function_name,
    role,
    timeout=None,
    memory_size=None,
    runtime=DEFAULT_RUNTIME,
    env_vars={},
    s3_code_bucket=None,
    verbose=True,
):
    """
    Create a lambda function with the given zipfile. If the zipfile is larger
    than 50 MB, you must specify an `s3_code_bucket`.
    """

    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    if not os.path.isfile(path_to_zipfile):
        raise ValueError(f"Zip file does not exist: {path_to_zipfile}")

    common_args = {
        "FunctionName": function_name,
        "Runtime": runtime,
        "Role": role,
        "Handler": handler,
        "Environment": {"Variables": env_vars},
    }
    if timeout is not None:
        common_args["Timeout"] = timeout
    if memory_size is not None:
        common_args["MemorySize"] = memory_size

    if needs_s3_upload(path_to_zipfile):
        if not s3_code_bucket:
            raise ValueError(
                "When zipfile is larger than 50 MB, s3_code_bucket is required"
            )
        temp_key = f"{function_name}_{random_string(10)}.zip"
        with temp_file_on_s3(
            local_path=path_to_zipfile,
            bucket=s3_code_bucket,
            key=temp_key,
            verbose=verbose,
        ):
            boto3.client("lambda").create_function(
                Code={"S3Bucket": s3_code_bucket, "S3Key": temp_key}, **common_args
            )
            pif("Lambda function created")
    else:
        with open(path_to_zipfile, "rb") as f:
            zipfile_contents = f.read()
        pif(f"Uploading {path_to_zipfile} to Lambda")
        boto3.client("lambda").create_function(
            Code={"ZipFile": zipfile_contents}, **common_args
        )
        pif("Lambda function created")


def perform_update(
    path_to_zipfile, function_name, s3_code_bucket=None, verbose=True,
):
    def pif(x):
        if verbose:
            print(x)

    if not os.path.isfile(path_to_zipfile):
        raise ValueError(f"Zip file does not exist: {path_to_zipfile}")

    common_args = {"FunctionName": function_name}

    if needs_s3_upload(path_to_zipfile):
        if not s3_code_bucket:
            raise ValueError(
                "When zipfile is larger than 50 MB, s3_code_bucket is required"
            )
        temp_key = f"{function_name}_{random_string(10)}.zip"
        with temp_file_on_s3(
            local_path=path_to_zipfile,
            bucket=s3_code_bucket,
            key=temp_key,
            verbose=verbose,
        ):
            boto3.client("lambda").update_function_code(
                S3Bucket=s3_code_bucket, S3Key=temp_key, **common_args
            )
            pif("Lambda function code updated")
    else:
        with open(path_to_zipfile, "rb") as f:
            zipfile_contents = f.read()
        pif(f"Uploading {path_to_zipfile} to Lambda")
        boto3.client("lambda").update_function_code(
            ZipFile=zipfile_contents, **common_args
        )
        pif("Lambda function code updated")
