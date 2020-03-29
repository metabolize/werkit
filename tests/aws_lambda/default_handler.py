import pytest
import pdb
import asyncio
import json

import werkit.aws_lambda.parallel 
from werkit.aws_lambda.default_handler import handler
import botocore.session
from botocore.stub import Stubber
from botocore.exceptions import ClientError

from unittest.mock import patch

import io

from tests.aws_lambda.worker.service import handler as worker_handler

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


def test_default_handler_success():
    stubber = init()

    expected_result = []
    for _input in input:
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
    stubber.activate()

    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)

    assert result == expected_result 


def test_default_handler_failure():
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
    stubber.activate()

    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)


    assert result[0]['exception'] == 'ClientError'
    assert result[1:] == expected_result
