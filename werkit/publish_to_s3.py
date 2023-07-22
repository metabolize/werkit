import os
import typing as t

from .common.cli_common import InferredFunctionEnvironment


def local_path_for_built_lambda(function_name: str) -> str:
    return os.path.join("lambdas", f"{function_name}.zip")


def local_path_for_manifest(function_name: str) -> str:
    return os.path.join("lambdas", f"{function_name}.manifest.json")


def _get_s3_key_base(
    function_name: str,
    version: t.Optional[str],
    sha1: t.Optional[str],
    with_manifest: bool,
) -> str:
    if version:
        return f"{function_name}/tags/{version}"
    else:
        return f"{function_name}/branches/{sha1}"


def s3_key_for_built_lambda(
    function_name: str,
    version: t.Optional[str] = None,
    sha1: t.Optional[str] = None,
    with_manifest: bool = False,
) -> str:
    return f"{_get_s3_key_base(function_name, version, sha1, with_manifest)}.zip"


def s3_key_for_manifest(
    function_name: str,
    version: t.Optional[str] = None,
    sha1: t.Optional[str] = None,
    with_manifest: bool = False,
) -> str:
    return (
        f"{_get_s3_key_base(function_name, version, sha1, with_manifest)}.manifest.json"
    )


def publish_file_to_s3(
    key: str, filename: str, bucket_name: str, verbose: bool
) -> None:
    import boto3

    client = boto3.client("s3")

    def exists() -> bool:
        try:
            client.head_object(Bucket=bucket_name, Key=key)
        except client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == 404:
                return True
        return False

    if exists():
        raise ValueError(f"s3://{bucket_name}/{key} already exists on S3")

    client.upload_file(
        Filename=filename,
        Bucket=bucket_name,
        Key=key,
    )


class PublishCommonKwargs(t.TypedDict):
    bucket_name: str
    verbose: bool


def perform_publish(
    environment: InferredFunctionEnvironment,
    verbose: bool,
    bucket_name: str,
    with_manifest: bool,
) -> None:
    function_name = environment.function_name
    version = environment.version
    sha1 = environment.sha1

    assert (version is not None) != (sha1 is not None)

    common_kwargs: PublishCommonKwargs = dict(
        bucket_name=bucket_name,
        verbose=verbose,
    )

    publish_file_to_s3(
        key=s3_key_for_built_lambda(
            function_name=function_name,
            version=version,
            sha1=sha1,
            with_manifest=with_manifest,
        ),
        filename=local_path_for_built_lambda(function_name=function_name),
        **common_kwargs,
    )

    if with_manifest:
        publish_file_to_s3(
            key=s3_key_for_manifest(
                function_name=function_name,
                version=version,
                sha1=sha1,
                with_manifest=with_manifest,
            ),
            filename=local_path_for_manifest(function_name=function_name),
            **common_kwargs,
        )
