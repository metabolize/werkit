#!/usr/bin/env python3
import os


def set_path() -> None:
    import sys

    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )


set_path()

import click  # noqa: E402

from werkit.common.cli_common import (  # noqa: E402
    infer_commit_from_ci_environment,
    infer_function_environment_from_ci_environment,
)
from werkit.publish_to_s3 import (  # noqa: E402
    perform_publish,
)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("-v", "--verbose", is_flag=True, default=True, help="Be extra talkative")
@click.option("-b", "--bucket-name", help="Archive bucket name", required=True)
@click.option(
    "--with-manifest/--without-manifest",
    help="Function inclues a manifest",
    default=False,
    is_flag=True,
)
def infer_and_publish(verbose: bool, bucket_name: str, with_manifest: bool) -> None:
    environment = infer_function_environment_from_ci_environment()
    perform_publish(
        environment=environment,
        verbose=verbose,
        bucket_name=bucket_name,
        with_manifest=with_manifest,
    )


@cli.command()
@click.option("-v", "--verbose", is_flag=True, default=True, help="Be extra talkative")
@click.option("-f", "--function-name", help="Function name", required=True)
@click.option("-b", "--bucket-name", help="Archive bucket name", required=True)
@click.option(
    "--with-manifest/--without-manifest",
    help="Function inclues a manifest",
    default=False,
    is_flag=True,
)
def publish_using_sha1(
    verbose: bool, function_name: str, bucket_name: str, with_manifest: bool
) -> None:
    environment = infer_commit_from_ci_environment(function_name)
    perform_publish(
        environment=environment,
        verbose=verbose,
        bucket_name=bucket_name,
        with_manifest=with_manifest,
    )


if __name__ == "__main__":
    cli()
