import pytest
import pdb
import asyncio
import json

import werkit.aws_lambda.parallel 
from werkit.aws_lambda.default_handler import handler
import botocore.session
from botocore.stub import Stubber
from botocore.exceptions import ClientError
from functools import partial

from unittest.mock import patch

import io

from tests.aws_lambda.worker.service import handler as worker_handler

from tests.aws_lambda.parallel import input, extra_args, lambda_worker_function_name, create_input_event, init, parallel_map_on_lambda_timeout_failure_call_worker_service_mock

def setup_mock_success_response(stubber, expected_result, _input):
    input_event = create_input_event(_input)
    _expected_output = worker_handler(input_event, None)
    expected_result.append(_expected_output)
    expected_output_payload = _expected_output
    expected_output = {
        'StatusCode': 200,
        'Payload' : io.StringIO(json.dumps(expected_output_payload))
    }

    stubber.add_response('invoke', expected_output, { 
        'FunctionName':lambda_worker_function_name,
        'Payload':json.dumps(input_event)
    })


def setup_mock_failure_response(stubber, _input):
    input_event = create_input_event(_input)
    stubber.add_client_error('invoke', expected_params={ 
        'FunctionName':lambda_worker_function_name,
        'Payload':json.dumps(input_event)
    })

def setup_first_failure_mock_responses(stubber):
    #make the first one fail
    _setup_mock_failure_response = partial(setup_mock_failure_response, stubber)
    for _input in input[:1]:
        _setup_mock_failure_response(_input)
        

    expected_result = []
    _setup_mock_success_response = partial(setup_mock_success_response, stubber, expected_result)
    for _input in input[1:]:
        _setup_mock_success_response(_input)

    return expected_result

def test_default_handler_success():
    stubber = init()

    expected_result = []
    _setup_mock_success_response = partial(setup_mock_success_response, stubber, expected_result)
    for _input in input:
        _setup_mock_success_response(_input)
    stubber.activate()

    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)

    assert result == expected_result 


def test_default_handler_client_failure():
    stubber = init()

    expected_results = setup_first_failure_mock_responses(stubber)
    stubber.activate()
    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)


    assert result[0]['exception'] == 'ClientError'
    assert result[1:] == expected_results


def test_default_handler_timeout_failure():
    stubber = init()

    call_worker_service_old = werkit.aws_lambda.parallel.call_worker_service
    werkit.aws_lambda.parallel.call_worker_service = parallel_map_on_lambda_timeout_failure_call_worker_service_mock

    setup_first_failure_mock_responses(stubber)
    stubber.activate()

    results = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name, timeout=1)

    assert all([r['exception'] == 'TimeoutError' for r in results])

    werkit.aws_lambda.parallel.call_worker_service = call_worker_service_old 
