#!/usr/bin/env python3

import click
from dotenv import load_dotenv
from werkit.aws_lambda.deploy import (
    create_orchestrator_function as _create_orchestrator_function,
    build_orchestrator_zip,
    _clean,
)

load_dotenv()


def build_dir_option(function):
    function = click.option(
        "--build-dir",
        default="build",
        help="Directory where orchestrator lambda function zip is built",
    )(function)
    return function


def common_options(function):
    function = build_dir_option(function)
    function = click.option(
        "--path-to-orchestrator-zip",
        default="build/orchestrator-function.zip",
        help="Orchestrator lambda zip function target location",
    )(function)
    function = click.option(
        "--worker-function-name",
        required=True,
        help="Name of the lambda worker function invoked by orchestrator",
        envvar="WORKER_FUNCTION_NAME",
        show_envvar=True,
    )(function)
    function = click.option(
        "--orchestrator-function-name",
        required=True,
        envvar="ORCHESTRATOR_FUNCTION_NAME",
        show_envvar=True,
        help="Name of the orchestrator lambda function",
    )(function)
    function = click.option(
        "--aws-role",
        required=True,
        help="AWS Role for the orchestrator lambda function",
        envvar="LAMBDA_ROLE",
        show_envvar=True,
    )(function)
    function = click.option(
        "--worker-timeout", default=600, help="Timeout for each worker function",
    )(function)
    function = click.option(
        "--orchestrator-timeout",
        default=600,
        help="Timeout of the orchestrator lambda function",
    )(function)
    return function


@click.group()
def cli():
    pass


@cli.command()
@build_dir_option
def clean(build_dir):
    _clean(build_dir)


@cli.command()
@common_options
def create_orchestrator_function(
    build_dir,
    aws_role,
    path_to_orchestrator_zip,
    worker_function_name,
    orchestrator_function_name,
    worker_timeout,
    orchestrator_timeout,
):
    import boto3

    client = boto3.client("lambda")
    build_orchestrator_zip(build_dir, path_to_orchestrator_zip)
    _create_orchestrator_function(
        aws_role,
        path_to_orchestrator_zip,
        client,
        worker_function_name,
        orchestrator_function_name,
        worker_timeout=worker_timeout,
        orchestrator_timeout=orchestrator_timeout,
    )


if __name__ == "__main__":
    cli()
