import werkit.aws_lambda.parallel
import botocore.session
from botocore.stub import Stubber
from functools import partial
import json
from tests.aws_lambda.worker.service import handler as worker_handler
import io
import asyncio

input = [1, 2, 3, 4]
extra_args = [2, 3]
lambda_worker_function_name = "test_worker"
default_timeout = 120


def setup_mock_success_response(stubber, expected_result, _input):
    input_event = create_input_event(_input)
    _expected_output = worker_handler(input_event, None)
    expected_result.append(_expected_output)
    expected_output_payload = _expected_output
    expected_output = {
        "StatusCode": 200,
        "Payload": io.StringIO(json.dumps(expected_output_payload)),
    }

    stubber.add_response(
        "invoke",
        expected_output,
        {
            "FunctionName": lambda_worker_function_name,
            "Payload": json.dumps(input_event),
        },
    )


def setup_mock_failure_response(stubber, _input):
    input_event = create_input_event(_input)
    stubber.add_client_error(
        "invoke",
        expected_params={
            "FunctionName": lambda_worker_function_name,
            "Payload": json.dumps(input_event),
        },
    )


def setup_first_failure_mock_responses():
    stubber = init()

    # make the first one fail
    _setup_mock_failure_response = partial(setup_mock_failure_response, stubber)
    for _input in input[:1]:
        _setup_mock_failure_response(_input)

    expected_result = []
    _setup_mock_success_response = partial(
        setup_mock_success_response, stubber, expected_result
    )
    for _input in input[1:]:
        _setup_mock_success_response(_input)

    stubber.activate()

    return expected_result


def setup_success_mock_responses():
    stubber = init()

    expected_result = []
    _setup_mock_success_response = partial(
        setup_mock_success_response, stubber, expected_result
    )
    for _input in input:
        _setup_mock_success_response(_input)
    stubber.activate()

    return expected_result


def create_input_event(_input):
    return {"input": _input, "extra_args": extra_args}


def init():
    client = botocore.session.get_session().create_client("lambda")
    werkit.aws_lambda.parallel.client = client
    stubber = Stubber(client)
    return stubber


async def parallel_map_on_lambda_timeout_failure_call_worker_service_mock(
    lambda_worker_function_name, extra_args, _input
):
    # introduce a timeout that will trigger a timeout error
    await asyncio.sleep(2)
    return worker_handler({"input": _input, "extra_args": extra_args})
