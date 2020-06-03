import asyncio
import json
from asynctest import CoroutineMock
from botocore.exceptions import ClientError
from .test_worker.service import handler as worker_handler

inputs = [1, 2, 3, 4]
extra_args = [2, 3]
lambda_worker_function_name = "test_worker"
default_timeout = 120


def setup_success_mock_responses(mock_invoke, _inputs):
    expected_result = []
    invoke_return_values = []
    for _input in _inputs:
        input_event = create_input_event(_input)
        _expected_output = worker_handler(input_event, None)
        expected_result.append(_expected_output)

        payload_mock = CoroutineMock()
        invoke_return_value = {"Payload": payload_mock}
        payload_mock.read = CoroutineMock()
        payload_mock.read.return_value = json.dumps(_expected_output).encode()

        invoke_return_values.append(invoke_return_value)

    m = CoroutineMock()
    m2 = CoroutineMock()
    m2.return_value = False
    mock_invoke.return_value.__aenter__ = m
    mock_invoke.return_value.__aexit__ = m2

    m.return_value.invoke = CoroutineMock()

    # setup mock
    m.return_value.invoke.side_effect = invoke_return_values

    return expected_result


def setup_mock_failure_response(mock_invoke, _input):
    m = CoroutineMock()
    m2 = CoroutineMock()
    mock_invoke.return_value.__aenter__ = m
    mock_invoke.return_value.__aexit__ = m2
    m2.return_value = False

    m.return_value.invoke = CoroutineMock()

    m.return_value.invoke.side_effect = ClientError({"Error": {}}, "")


def setup_first_failure_mock_responses(mock_invoke, _inputs):
    m = CoroutineMock()
    m2 = CoroutineMock()
    mock_invoke.return_value.__aenter__ = m
    mock_invoke.return_value.__aexit__ = m2
    m2.return_value = False

    expected_result = []
    invoke_return_values = [ClientError({"Error": {}}, "")]  # make the first one fail
    for _input in _inputs[1:]:
        input_event = create_input_event(_input)
        _expected_output = worker_handler(input_event, None)
        expected_result.append(_expected_output)

        payload_mock = CoroutineMock()
        invoke_return_value = {"Payload": payload_mock}
        payload_mock.read = CoroutineMock()
        payload_mock.read.return_value = json.dumps(_expected_output).encode()

        invoke_return_values.append(invoke_return_value)

    m.return_value.invoke = CoroutineMock()

    # setup mock
    m.return_value.invoke.side_effect = invoke_return_values

    return expected_result


def create_input_event(_input):
    return {"input": _input, "extra_args": extra_args}


async def parallel_map_on_lambda_timeout_failure_call_worker_service_mock(
    lambda_worker_function_name, extra_args, _input, with_timing=False
):
    # introduce a timeout that will trigger a timeout error
    await asyncio.sleep(2)
    return worker_handler({"input": _input, "extra_args": extra_args})
