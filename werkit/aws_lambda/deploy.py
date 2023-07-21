import os
import sys
import typing as t
import boto3
from ..s3 import temp_file_on_s3

if t.TYPE_CHECKING:
    from mypy_boto3_s3.literals import RegionName
    from mypy_boto3_lambda.literals import RuntimeType
    from mypy_boto3_lambda.type_defs import FunctionCodeTypeDef


def default_runtime() -> "RuntimeType":
    import sys

    return t.cast(
        "RuntimeType", f"python{sys.version_info.major}.{sys.version_info.minor}"
    )


def needs_s3_upload(path_to_zipfile: str) -> bool:
    return os.path.getsize(path_to_zipfile) > 50 * 2**20


def _create_or_update(
    local_path_to_zipfile: t.Optional[str],
    s3_path_to_zipfile: t.Optional[str],
    message: str,
    create_or_update_fn: t.Callable[["FunctionCodeTypeDef"], None],
    verbose: bool = False,
    s3_code_bucket: t.Optional[str] = None,
    force_upload_to_s3_code_bucket: bool = False,
) -> None:
    """
    Create or update a lambda function with the given zipfile. If the zipfile is larger
    than 50 MB, you must specify an `s3_code_bucket`.
    """
    if bool(local_path_to_zipfile) == bool(s3_path_to_zipfile):
        raise ValueError(
            "Either `local_path_to_zipfile` or `s3_path_to_zipfile` must be provided (and not both)"
        )

    def pif(x: str) -> None:
        if verbose:
            print(x, file=sys.stderr)

    if s3_path_to_zipfile:
        if s3_code_bucket is None:
            raise ValueError(
                "When `s3_path_to_zipfile` is provided, `s3_code_bucket` is required"
            )
        create_or_update_fn({"S3Bucket": s3_code_bucket, "S3Key": s3_path_to_zipfile})
        pif(message)
        return

    if local_path_to_zipfile is None:
        raise ValueError("Shouldn't get here")

    if not os.path.isfile(local_path_to_zipfile):
        raise ValueError(f"Local zip file does not exist: {local_path_to_zipfile}")

    if needs_s3_upload(local_path_to_zipfile) or force_upload_to_s3_code_bucket:
        if s3_code_bucket is None:
            raise ValueError(
                """
                When zipfile is larger than 50 MB,
                or force_upload_to_s3_code_bucket is True,
                then s3_code_bucket is required
                """
            )
        with temp_file_on_s3(
            local_path=local_path_to_zipfile, bucket=s3_code_bucket, verbose=verbose
        ) as temp_key:
            create_or_update_fn({"S3Bucket": s3_code_bucket, "S3Key": temp_key})
            pif(message)
    else:
        with open(local_path_to_zipfile, "rb") as f:
            zipfile_contents = f.read()
        pif(f"Uploading {local_path_to_zipfile} to Lambda")
        create_or_update_fn({"ZipFile": zipfile_contents})
        pif(message)


def perform_create(
    aws_region: "RegionName",
    handler: str,
    function_name: str,
    role: str,
    local_path_to_zipfile: t.Optional[str] = None,
    s3_path_to_zipfile: t.Optional[str] = None,
    timeout: t.Optional[int] = None,
    memory_size: t.Optional[int] = None,
    runtime: t.Optional["RuntimeType"] = None,
    env_vars: dict[str, str] = {},
    s3_code_bucket: t.Optional[str] = None,
    verbose: bool = False,
    force_upload_to_s3_code_bucket: bool = False,
    wait_until_active: bool = True,
    wait_until_active_timeout_seconds: int = 30,
) -> None:
    if bool(local_path_to_zipfile) == bool(s3_path_to_zipfile):
        raise ValueError(
            "Either `local_path_to_zipfile` or `s3_path_to_zipfile` must be provided (and not both)"
        )

    client = boto3.client("lambda", region_name=aws_region)

    def create(code_arguments: "FunctionCodeTypeDef") -> None:
        extra_options = {}
        if timeout is not None:
            extra_options["Timeout"] = timeout
        if memory_size is not None:
            extra_options["MemorySize"] = memory_size

        client.create_function(
            FunctionName=function_name,
            Runtime=runtime or default_runtime(),
            Role=role,
            Handler=handler,
            Environment={"Variables": env_vars},
            Code=code_arguments,
            **extra_options,  # type: ignore[arg-type]
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

    if wait_until_active:
        client.get_waiter("function_active").wait(
            FunctionName=function_name,
            WaiterConfig={
                "Delay": 1,
                "MaxAttempts": wait_until_active_timeout_seconds,
            },
        )


def perform_update_code(
    aws_region: "RegionName",
    function_name: str,
    local_path_to_zipfile: t.Optional[str] = None,
    s3_path_to_zipfile: t.Optional[str] = None,
    s3_code_bucket: t.Optional[str] = None,
    verbose: bool = False,
    force_upload_to_s3_code_bucket: bool = False,
    wait_until_updated: bool = True,
    wait_until_updated_timeout_seconds: int = 30,
) -> None:
    if bool(local_path_to_zipfile) == bool(s3_path_to_zipfile):
        raise ValueError(
            "Either `local_path_to_zipfile` or `s3_path_to_zipfile` must be provided (and not both)"
        )

    client = boto3.client("lambda", region_name=aws_region)

    def update(code_arguments: "FunctionCodeTypeDef") -> None:
        client.update_function_code(FunctionName=function_name, **code_arguments)

    _create_or_update(
        local_path_to_zipfile=local_path_to_zipfile,
        s3_path_to_zipfile=s3_path_to_zipfile,
        message="Lambda function code updated",
        create_or_update_fn=update,
        verbose=verbose,
        s3_code_bucket=s3_code_bucket,
        force_upload_to_s3_code_bucket=force_upload_to_s3_code_bucket,
    )

    if wait_until_updated:
        client.get_waiter("function_updated").wait(
            FunctionName=function_name,
            WaiterConfig={
                "Delay": 1,
                "MaxAttempts": wait_until_updated_timeout_seconds,
            },
        )
