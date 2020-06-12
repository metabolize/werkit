import os
import sys
import boto3
from ..s3 import temp_file_on_s3

DEFAULT_RUNTIME = "python3.7"


def needs_s3_upload(path_to_zipfile):
    return os.path.getsize(path_to_zipfile) > 50 * 2 ** 20


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
    verbose=False,
):
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

    def create(code_arguments):
        boto3.client("lambda").create_function(Code=code_arguments, **common_args)

    create_or_update_lambda(
        path_to_zipfile=path_to_zipfile,
        function_name=function_name,
        message="Lambda function created",
        boto3_function=create,
        verbose=verbose,
        s3_code_bucket=s3_code_bucket,
    )


def perform_update_code(
    path_to_zipfile, function_name, s3_code_bucket=None, verbose=False,
):
    common_args = {"FunctionName": function_name}

    def update(code_arguments):
        boto3.client("lambda").update_function_code(**code_arguments, **common_args)

    create_or_update_lambda(
        path_to_zipfile=path_to_zipfile,
        function_name=function_name,
        message="Lambda function code updated",
        boto3_function=update,
        verbose=verbose,
        s3_code_bucket=s3_code_bucket,
    )


def create_or_update_lambda(
    path_to_zipfile,
    function_name,
    message,
    boto3_function,
    verbose=False,
    s3_code_bucket=None,
):
    """
    Create or update a lambda function with the given zipfile. If the zipfile is larger
    than 50 MB, you must specify an `s3_code_bucket`.
    """

    def pif(x):
        if verbose:
            print(x, file=sys.stderr)

    if not os.path.isfile(path_to_zipfile):
        raise ValueError(f"Zip file does not exist: {path_to_zipfile}")

    if needs_s3_upload(path_to_zipfile):
        if not s3_code_bucket:
            raise ValueError(
                "When zipfile is larger than 50 MB, s3_code_bucket is required"
            )
        with temp_file_on_s3(
            local_path=path_to_zipfile, bucket=s3_code_bucket, verbose=verbose,
        ) as temp_key:
            boto3_function({"S3Bucket": s3_code_bucket, "S3Key": temp_key})
            pif(message)
    else:
        with open(path_to_zipfile, "rb") as f:
            zipfile_contents = f.read()
        pif(f"Uploading {path_to_zipfile} to Lambda")
        boto3_function({"ZipFile": zipfile_contents})
        pif(message)
