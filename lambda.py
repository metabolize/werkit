#!/usr/bin/env python3

import shutil
import click
from dotenv import load_dotenv
from werkit.aws_lambda.orchestrator_deploy import (
    deploy_orchestrator,
    update_orchestrator_code,
)

load_dotenv()

BUILD_DIR = "build"


@click.group()
def cli():
    pass


def _clean():
    shutil.rmtree(BUILD_DIR, ignore_errors=True)


@cli.command()
def clean():
    _clean()


def common_options(function):
    function = click.option(
        "--path-to-orchestrator-zip",
        default="build/orchestrator-function.zip",
        help="Orchestrator lambda zip function target location",
    )(function)
    function = click.option(
        "--orchestrator-function-name",
        required=True,
        envvar="ORCHESTRATOR_FUNCTION_NAME",
        show_envvar=True,
        help="Name of the orchestrator lambda function",
    )(function)
    function = click.option(
        "--s3-code-bucket", default=None, help="S3 bucket where code is uploaded"
    )(function)
    function = click.option("--verbose", default=False, help="Enable verbose output")(
        function
    )
    return function


def deploy_options(function):
    function = click.option(
        "--worker-function-name",
        required=True,
        help="Name of the lambda worker function invoked by orchestrator",
        envvar="WORKER_FUNCTION_NAME",
        show_envvar=True,
    )(function)
    function = click.option(
        "--role",
        required=True,
        help="AWS Role for the orchestrator lambda function",
        envvar="LAMBDA_ROLE",
        show_envvar=True,
    )(function)
    function = click.option(
        "--worker-timeout", default=600, help="Timeout for each worker function"
    )(function)
    function = click.option(
        "--orchestrator-timeout",
        default=600,
        help="Timeout of the orchestrator lambda function",
    )(function)
    return function


@cli.command()
@common_options
@deploy_options
def deploy(
    path_to_orchestrator_zip,
    orchestrator_function_name,
    s3_code_bucket,
    verbose,
    role,
    worker_function_name,
    worker_timeout,
    orchestrator_timeout,
):
    _clean()
    deploy_orchestrator(
        build_dir=BUILD_DIR,
        path_to_orchestrator_zip=path_to_orchestrator_zip,
        orchestrator_function_name=orchestrator_function_name,
        role=role,
        orchestrator_timeout=orchestrator_timeout,
        worker_function_name=worker_function_name,
        worker_timeout=worker_timeout,
        s3_code_bucket=s3_code_bucket,
    )


@cli.command()
@common_options
def update_code(
    path_to_orchestrator_zip, orchestrator_function_name, s3_code_bucket, verbose
):
    _clean()
    update_orchestrator_code(
        build_dir=BUILD_DIR,
        path_to_orchestrator_zip=path_to_orchestrator_zip,
        orchestrator_function_name=orchestrator_function_name,
        s3_code_bucket=s3_code_bucket,
    )


if __name__ == "__main__":
    cli()
