import os
import uuid
import boto3
from dotenv import load_dotenv
import pytest
from .build import create_zipfile_from_dir
from .deploy import perform_create
from .orchestrator_deploy import deploy_orchestrator


load_dotenv()


def role():
    """
    This role must have the following policy: AWSLambdaRole.
    """
    return os.environ["INTEGRATION_TEST_LAMBDA_ROLE"]


# TODO: Reuse the zip files across tests.
def create_test_functions(
    tmpdir, worker_timeout=None, worker_delay=None, worker_should_throw=False
):
    unique = uuid.uuid4().hex
    worker_function_name = f"werkit_integ_test_worker_{unique}"
    orchestrator_function_name = f"werkit_integ_test_orchestrator_{unique}"

    path_to_worker_zip = str(tmpdir / "worker.zip")
    create_zipfile_from_dir(
        dir_path="werkit/aws_lambda/test_worker/", path_to_zipfile=path_to_worker_zip,
    )
    env_vars = {}
    if worker_delay:
        env_vars["DELAY_SECONDS"] = str(worker_delay)
    if worker_should_throw:
        env_vars["SHOULD_THROW"] = "TRUE"
    perform_create(
        path_to_zipfile=path_to_worker_zip,
        handler="service.handler",
        function_name=worker_function_name,
        role=role(),
        timeout=10,
        env_vars=env_vars,
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


@pytest.mark.slow
def test_integration_success(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir
    )

    try:
        data = invoke_orchestrator(orchestrator_function_name)
        print(data)

        # If ths following assertion fails, it's because the service does not
        # use the werkit manager to handle exceptions.
        assert set(data.keys()) == set(
            ["results", "orchestrator_duration_seconds", "start_timestamp"]
        )
        assert isinstance(data["orchestrator_duration_seconds"], float)
        assert isinstance(data["start_timestamp"], float)

        results = data["results"]
        assert isinstance(results, list)
        assert all([r["success"] is True for r in results])
        assert [r["result"] for r in results] == [6, 7, 8, 9]
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)


@pytest.mark.slow
def test_integration_unhandled_exception(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir, worker_should_throw=True
    )

    try:
        data = invoke_orchestrator(orchestrator_function_name)
        print(data)

        assert set(data.keys()) == set(
            ["results", "orchestrator_duration_seconds", "start_timestamp"]
        )
        assert isinstance(data["orchestrator_duration_seconds"], float)
        assert isinstance(data["start_timestamp"], float)

        results = data["results"]
        assert all([r["success"] is False for r in results])
        assert all([r["error_origin"] == "system" for r in results])
        assert all(
            [
                r["error"]
                == [
                    '  File "/var/task/service.py", line 36, in handler\n    raise Exception("Whoops!")\n',
                    "Exception: Whoops!",
                ]
                for r in results
            ]
        )
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)


@pytest.mark.slow
def test_integration_timeout_failure(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir, worker_timeout=1, worker_delay=3,
    )

    try:
        data = invoke_orchestrator(orchestrator_function_name)
        print(data)

        assert set(data.keys()) == set(
            ["results", "orchestrator_duration_seconds", "start_timestamp"]
        )
        assert isinstance(data["orchestrator_duration_seconds"], float)
        assert isinstance(data["start_timestamp"], float)

        results = data["results"]
        assert all([r["success"] is False for r in results])
        assert all([r["error_origin"] == "orchestration" for r in results])
        assert all(
            [
                r["error"][-1] == "concurrent.futures._base.TimeoutError\n"
                for r in results
            ]
        )
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)
