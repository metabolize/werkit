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


from tests.aws_lambda.util import input,\
    extra_args,\
    lambda_worker_function_name,\
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,\
    setup_first_failure_mock_responses,\
    setup_success_mock_responses

def test_default_handler_success():

    expected_result = setup_success_mock_responses()

    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)

    assert result == expected_result 


def test_default_handler_client_failure():
    expected_results = setup_first_failure_mock_responses()
    result = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name)


    assert result[0]['exception'] == 'ClientError'
    assert result[1:] == expected_results


def test_default_handler_timeout_failure():

    call_worker_service_old = werkit.aws_lambda.parallel.call_worker_service
    werkit.aws_lambda.parallel.call_worker_service = parallel_map_on_lambda_timeout_failure_call_worker_service_mock

    setup_success_mock_responses()
    results = handler({'input':input, 'extra_args':extra_args}, None, lambda_worker_function_name=lambda_worker_function_name, timeout=1)

    assert all([r['exception'] == 'TimeoutError' for r in results])

    werkit.aws_lambda.parallel.call_worker_service = call_worker_service_old 

