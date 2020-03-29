import pytest
import pdb
import asyncio
import json

import werkit.aws_lambda.parallel 
import botocore.session
from botocore.stub import Stubber
from botocore.exceptions import ClientError

from unittest.mock import patch

import io

from tests.aws_lambda.worker.service import handler

#TODO: figure out how to get patch to work

input = [1, 2, 3, 4]
extra_args = [2, 3]

lambda_worker_function_name = 'test_worker'

def create_input_event(_input):
    return {'input': _input, 'extra_args': extra_args}

def init():
    client = botocore.session.get_session().create_client('lambda')
    werkit.aws_lambda.parallel.client = client
    stubber = Stubber(client)
    return stubber


# test that we expect to get a successful response out
def test_call_worker_service_success():
    stubber = init()
    _input = input[0]
    input_event = create_input_event(_input)
    expected_output_payload = handler(input_event, None)
    expected_output = {
        'StatusCode': 200,
        'Payload' : io.StringIO(json.dumps(expected_output_payload))
    }

    stubber.add_response('invoke', expected_output, { 
        'FunctionName':lambda_worker_function_name,
        'Payload':json.dumps(input_event)
    })
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(werkit.aws_lambda.parallel.call_worker_service(lambda_worker_function_name, extra_args, _input))

    assert result == expected_output_payload 

# test that we expect to get a client error
def test_call_worker_service_failure():
    stubber = init()
    _input = input[0]
    input_event = create_input_event(_input)
    stubber.add_client_error('invoke',expected_params={ 
        'FunctionName':lambda_worker_function_name,
        'Payload':json.dumps(input_event)
    })
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    with pytest.raises(ClientError):
        event_loop.run_until_complete(werkit.aws_lambda.parallel.call_worker_service(lambda_worker_function_name, extra_args, _input))


def test_parallel_map_on_lambda_success():
    stubber = init()

    expected_result = []
    for _input in input:
        input_event = create_input_event(_input)
        _expected_output = handler(input_event, None)
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
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(werkit.aws_lambda.parallel.parallel_map_on_lambda(lambda_worker_function_name, input, extra_args))

    assert result == expected_result 


def test_parallel_map_on_lambda_failure():
    stubber = init()

    expected_result = []
    #make the first one fail
    for _input in input[:1]:
        input_event = create_input_event(_input)
        stubber.add_client_error('invoke', expected_params={ 
            'FunctionName':lambda_worker_function_name,
            'Payload':json.dumps(input_event)
        })

    for _input in input[1:]:
        input_event = create_input_event(_input)
        _expected_output = handler(input_event, None)
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
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(werkit.aws_lambda.parallel.parallel_map_on_lambda(lambda_worker_function_name, input, extra_args))

    assert isinstance(result[0], ClientError)
    assert result[1:] == expected_result

test_parallel_map_on_lambda_failure()
