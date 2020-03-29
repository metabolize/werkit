import pdb
import asyncio
import os
import json

import botocore.session
from botocore.stub import Stubber

from unittest.mock import patch

import io

#TODO: figure out how to get patch to work

input = [1, 2, 3, 4]
extra_args = [2,3]

def test_call_worker_service_success():
    lambda_worker_function_name = 'test_worker'
    os.environ['LAMBDA_WORKER_FUNCTION_NAME'] = lambda_worker_function_name 
    import werkit.aws_lambda.parallel 
    
    _input = input[0]
    client = botocore.session.get_session().create_client('lambda')
    werkit.aws_lambda.parallel.client = client
    stubber = Stubber(client)
    input_event = {'input': _input, 'extra_args': extra_args}
    expected_output_payload = '6'
    expected_output = {
        'StatusCode': 200,
        'Payload' : io.StringIO(json.dumps({'Response': expected_output_payload}))
    }

    stubber.add_response('invoke', expected_output, { 
        'FunctionName':lambda_worker_function_name,
        'Payload':json.dumps(input_event, sort_keys=True)
    })
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(werkit.aws_lambda.parallel.call_worker_service(_input, extra_args))

    assert result['Response'] == expected_output_payload 

def test_call_worker_service_failure():
    pass

