import os
import uuid
import boto3
from dotenv import load_dotenv
import pytest
from werkit.aws_lambda.build import create_zipfile_from_dir
from werkit.aws_lambda.deploy import perform_create
from werkit.orchestrator.deploy import deploy_orchestrator

from ..orchestrator_lambda.handler import schema


load_dotenv()

AWS_REGION = "us-east-1"


def role():
    """
    The role is accessed inside a function so pytest can import the module
    without triggering a KeyError.

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
    print(f"Unique worker function: {worker_function_name}")
    print(f"Unique orchestrator function: {orchestrator_function_name}")

    path_to_worker_zip = str(tmpdir / "worker.zip")
    create_zipfile_from_dir(
        dir_path="werkit/orchestrator/testing/worker_service/",
        path_to_zipfile=path_to_worker_zip,
    )
    env_vars = {}
    if worker_delay:
        env_vars["DELAY_SECONDS"] = str(worker_delay)
    if worker_should_throw:
        env_vars["SHOULD_THROW"] = "TRUE"
    perform_create(
        aws_region=AWS_REGION,
        local_path_to_zipfile=path_to_worker_zip,
        handler="handler.handler",
        function_name=worker_function_name,
        role=role(),
        timeout=10,
        env_vars=env_vars,
    )

    deploy_orchestrator(
        aws_region=AWS_REGION,
        build_dir=str(tmpdir / "build"),
        path_to_orchestrator_zip=str(tmpdir / "orchestrator.zip"),
        orchestrator_function_name=orchestrator_function_name,
        role=role(),
        worker_function_name=worker_function_name,
        worker_timeout=worker_timeout,
    )

    return worker_function_name, orchestrator_function_name


EXAMPLE_MESSAGE_KEY = {"someParameters": ["just", "a", "message", "key", "nbd"]}


def invoke_orchestrator(orchestrator_function_name):
    import json

    message = {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "itemPropertyName": "exponent",
        "itemCollection": {
            "first": 1,
            "second": 2,
            "tenth": 10,
            "twentieth": 20,
        },
        "commonInput": {"base": 2},
    }
    # Confidence check.
    schema.input_message.validate(message)
    response = boto3.client("lambda").invoke(
        FunctionName=orchestrator_function_name,
        Payload=json.dumps(message),
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

        schema.output_message.validate(data)

        result = data["result"]
        print(result)
        assert isinstance(result, object)
        assert all([r["success"] is True for r in result.values()])
        assert {k: r["result"] for k, r in result.items()} == {
            "first": 2**1,
            "second": 2**2,
            "tenth": 2**10,
            "twentieth": 2**20,
        }
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

        schema.output_message.validate(data)

        result = data["result"]
        assert set(result.keys()) == set(["first", "second", "tenth", "twentieth"])
        assert all([r["success"] is False for r in result.values()])
        assert all([r["error_origin"] == "system" for r in result.values()])
        assert all(
            [
                len(r["error"]) == 2
                and 'raise Exception("Whoops!")' in r["error"][0]
                and r["error"][1] == "Exception: Whoops!"
                for r in result.values()
            ]
        )
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)


@pytest.mark.slow
def test_integration_timeout_failure(tmpdir):
    worker_function_name, orchestrator_function_name = create_test_functions(
        tmpdir=tmpdir, worker_timeout=1, worker_delay=3
    )

    try:
        data = invoke_orchestrator(orchestrator_function_name)
        print(data)

        schema.output_message.validate(data)

        result = data["result"]
        assert set(result.keys()) == set(["first", "second", "tenth", "twentieth"])
        assert all([r["success"] is False for r in result.values()])
        assert all([r["error_origin"] == "orchestration" for r in result.values()])
        assert all(
            [
                r["error"][-1] == "concurrent.futures._base.TimeoutError\n"
                for r in result.values()
            ]
        )
    finally:
        client = boto3.client("lambda")
        client.delete_function(FunctionName=worker_function_name)
        client.delete_function(FunctionName=orchestrator_function_name)
