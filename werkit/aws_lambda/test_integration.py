import os
import boto3
import uuid
import tempfile
from pprint import pprint
import pytest
from .build import (
    create_venv_with_dependencies,
    collect_zipfile_contents,
    create_zipfile_from_dir,
)
from .deploy import perform_create
from .orchestrator_deploy import deploy_orchestrator


def role():
    """
    This role must have the following policy: AWSLambdaRole.
    """
    return os.environ["INTEGRATION_TEST_LAMBDA_ROLE"]


def create_test_functions(tmpdir, worker_timeout=None, worker_delay=None):
    unique = uuid.uuid4().hex
    worker_function_name = f"werkit_integ_test_worker_{unique}"
    orchestrator_function_name = f"werkit_integ_test_orchestrator_{unique}"

    path_to_worker_zip = str(tmpdir / "worker.zip")
    create_zipfile_from_dir(
        dir_path="werkit/aws_lambda/test_worker/", path_to_zipfile=path_to_worker_zip,
    )
    perform_create(
        path_to_zipfile=path_to_worker_zip,
        handler="service.handler",
        function_name=worker_function_name,
        role=role(),
        timeout=10,
        env_vars={"LAMBDA_WORKER_DELAY_SECONDS": str(worker_delay)}
        if worker_delay
        else {},
    )

    deploy_orchestrator(
        build_dir=str(tmpdir / "build"),
        path_to_orchestrator_zip=str(tmpdir / "orchestrator.zip"),
        orchestrator_function_name=orchestrator_function_name,
        role=role(),
        worker_function_name=worker_function_name,
        worker_timeout=worker_timeout,
    )

    return worker_function_name, orchestrator_function_name


def invoke_orchestrator(orchestrator_function_name):
    import json

    response = boto3.client("lambda").invoke(
        FunctionName=orchestrator_function_name,
        Payload=json.dumps({"input": [1, 2, 3, 4], "extra_args": [2, 3]}),
    )
    return json.load(response["Payload"])


def test_integration_success(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir
    )

    try:
        results = invoke_orchestrator(orchestrator_function_name)
        print(results)
        assert results == [6, 7, 8, 9]
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)


def test_integration_timeout_failure(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir, worker_timeout=1, worker_delay=3,
    )

    try:
        results = invoke_orchestrator(orchestrator_function_name)
        print(results)
        assert all([r["exception"] == "TimeoutError" for r in results])
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)
