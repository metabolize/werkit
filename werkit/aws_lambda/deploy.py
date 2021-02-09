import os
import sys
import boto3
from ..s3 import temp_file_on_s3

DEFAULT_RUNTIME = "python3.7"


def needs_s3_upload(path_to_zipfile):
    return os.path.getsize(path_to_zipfile) > 50 * 2 ** 20


def _create_or_update(
    local_path_to_zipfile,
    s3_path_to_zipfile,
    message,
    create_or_update_fn,
    verbose=False,
    s3_code_bucket=None,
    force_upload_to_s3_code_bucket=False,
):
    """
    Create or update a lambda function with the given zipfile. If the zipfile is larger
    than 50 MB, you must specify an `s3_code_bucket`.
    """
    if s3_path_to_zipfile and not s3_code_bucket:
        raise ValueError(
            "When `s3_path_to_zipfile` is provided, `s3_code_bucket` is required"
        )

    should_upload_directly_to_lambda = (
        local_path_to_zipfile
        and not force_upload_to_s3_code_bucket
        and not needs_s3_upload(local_path_to_zipfile)
    )

    if not should_upload_directly_to_lambda and not s3_code_bucket:
        raise ValueError(
            """
            When zipfile is larger than 50 MB,
            or force_upload_to_s3_code_bucket is True,
            then s3_code_bucket is required
            """
        )

    if local_path_to_zipfile and not os.path.isfile(local_path_to_zipfile):
        raise ValueError(f"Local zip file does not exist: {local_path_to_zipfile}")

    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    if should_upload_directly_to_lambda:
        with open(local_path_to_zipfile, "rb") as f:
            zipfile_contents = f.read()
        pif(f"Uploading {local_path_to_zipfile} to Lambda")
        create_or_update_fn({"ZipFile": zipfile_contents})
        pif(message)
    elif s3_path_to_zipfile:
        create_or_update_fn({"S3Bucket": s3_code_bucket, "S3Key": s3_path_to_zipfile})
        pif(message)
    else:
        with temp_file_on_s3(
            local_path=local_path_to_zipfile, bucket=s3_code_bucket, verbose=verbose
        ) as temp_key:
            create_or_update_fn({"S3Bucket": s3_code_bucket, "S3Key": temp_key})
            pif(message)


def perform_create(
    aws_region,
    handler,
    function_name,
    role,
    local_path_to_zipfile=None,
    s3_path_to_zipfile=None,
    timeout=None,
    memory_size=None,
    runtime=DEFAULT_RUNTIME,
    env_vars={},
    s3_code_bucket=None,
    verbose=False,
    force_upload_to_s3_code_bucket=False,
):
    if bool(local_path_to_zipfile) == bool(s3_path_to_zipfile):
        raise ValueError(
            "Either `local_path_to_zipfile` or `s3_path_to_zipfile` must be provided (and not both)"
        )

    def create(code_arguments):
        extra_options = {}
        if timeout is not None:
            extra_options["Timeout"] = timeout
        if memory_size is not None:
            extra_options["MemorySize"] = memory_size

        boto3.client("lambda", region_name=aws_region).create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role,
            Handler=handler,
            Environment={"Variables": env_vars},
            Code=code_arguments,
            **extra_options,
        )

    _create_or_update(
        local_path_to_zipfile=local_path_to_zipfile,
        s3_path_to_zipfile=s3_path_to_zipfile,
        message="Lambda function created",
        create_or_update_fn=create,
        verbose=verbose,
        s3_code_bucket=s3_code_bucket,
        force_upload_to_s3_code_bucket=force_upload_to_s3_code_bucket,
    )


def perform_update_code(
    aws_region,
    function_name,
    local_path_to_zipfile=None,
    s3_path_to_zipfile=None,
    s3_code_bucket=None,
    verbose=False,
    force_upload_to_s3_code_bucket=False,
):
    if bool(local_path_to_zipfile) == bool(s3_path_to_zipfile):
        raise ValueError(
            "Either `local_path_to_zipfile` or `s3_path_to_zipfile` must be provided (and not both)"
        )

    def update(code_arguments):
        boto3.client("lambda", region_name=aws_region).update_function_code(
            FunctionName=function_name, **code_arguments
        )

    _create_or_update(
        local_path_to_zipfile=local_path_to_zipfile,
        s3_path_to_zipfile=s3_path_to_zipfile,
        message="Lambda function code updated",
        create_or_update_fn=update,
        verbose=verbose,
        s3_code_bucket=s3_code_bucket,
        force_upload_to_s3_code_bucket=force_upload_to_s3_code_bucket,
    )
