import os
import base64
import boto3
import uuid
import zipfile
import tempfile
import json
from pprint import pprint
from werkit.aws_lambda.deploy import build_orchestrator_zip, create_orchestrator_function as _create_orchestrator_function

role = "arn:aws:iam::139234625917:role/werkit-test-integration"
# This role has the following policy: AWSLambdaRole

path_to_orchestrator_zip = "/tmp/python-orchestrator.zip"
path_to_worker_zip = "/tmp/python-worker.zip"

def create_worker_function(client, worker_filename, delay=None):
    environment = {"Variables": {}}
    if delay:
        environment["Variables"]["LAMBDA_WORKER_DELAY_SECONDS"] = str(delay)

    # create the worker function
    zipf = zipfile.ZipFile(
        path_to_worker_zip, "w", zipfile.ZIP_DEFLATED
    )  # TODO: make this a tempfile
    path = "werkit/aws_lambda/test_worker/"
    filename = worker_filename + ".py"
    zipf.write(os.path.join(path, filename), arcname=filename)
    zipf.close()

    with open(path_to_worker_zip, "rb") as f:
        bytes = f.read()

    worker_function_name = uuid.uuid4().hex
    response = client.create_function(
        FunctionName=worker_function_name,
        Runtime="python3.7",
        Role=role,  # FIXME: new role name
        Handler=worker_filename + ".handler",
        Code={"ZipFile": bytes},
        Environment=environment,
        Timeout=10,
    )
    # pprint(response)
    return worker_function_name, response


def create_orchestrator_function(client, worker_function_name, worker_timeout=None):
    build_orchestrator_zip('build', path_to_orchestrator_zip)
    orchestrator_function_name = uuid.uuid4().hex   #generate a name for the test function
    response = _create_orchestrator_function(role, path_to_orchestrator_zip, client, worker_function_name, orchestrator_function_name, worker_timeout=worker_timeout)
    return orchestrator_function_name, response 


def invoke_orchestrator(client, orchestrator_function_name):
    response = client.invoke(
        FunctionName=orchestrator_function_name,
        Payload=json.dumps({"input": [1, 2, 3, 4], "extra_args": [2, 3]}),
    )
    return response


def cleanup(client, worker_function_name, orchestrator_function_name):
    # cleanup: tear down the worker, and orchestrator functions
    worker_response = client.delete_function(FunctionName=worker_function_name)

    orchestrator_response = client.delete_function(
        FunctionName=orchestrator_function_name
    )

    return worker_response, orchestrator_response


def test_integration_success():
    client = boto3.client("lambda")

    worker_function_name, response = create_worker_function(client, "service")
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 201

    orchestrator_function_name, response = create_orchestrator_function(
        client, worker_function_name
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 201

    response = invoke_orchestrator(client, orchestrator_function_name)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    results = json.load(response["Payload"])
    print(results)
    assert results == [6, 7, 8, 9]

    worker_response, orchestrator_response = cleanup(
        client, worker_function_name, orchestrator_function_name
    )
    assert worker_response["ResponseMetadata"]["HTTPStatusCode"] == 204
    assert orchestrator_response["ResponseMetadata"]["HTTPStatusCode"] == 204


def test_integration_timeout_failure():
    client = boto3.client("lambda")

    worker_function_name, response = create_worker_function(client, "service", delay=3)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 201
    print("worker_function_name", worker_function_name)

    orchestrator_function_name, response = create_orchestrator_function(
        client, worker_function_name, worker_timeout=1
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 201
    print("orchestrator_function_name", orchestrator_function_name)

    response = invoke_orchestrator(client, orchestrator_function_name)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    print(response)
    results = json.load(response["Payload"])
    print(results)
    assert all([r["exception"] == "TimeoutError" for r in results])

    worker_response, orchestrator_response = cleanup(
        client, worker_function_name, orchestrator_function_name
    )
    assert worker_response["ResponseMetadata"]["HTTPStatusCode"] == 204
    assert orchestrator_response["ResponseMetadata"]["HTTPStatusCode"] == 204
