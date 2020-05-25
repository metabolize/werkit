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
from asynctest import Mock, patch

from werkit.aws_lambda.test_util import (
    inputs,
    extra_args,
    lambda_worker_function_name,
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
    setup_first_failure_mock_responses,
    setup_success_mock_responses,
)

call_handler = partial(
    handler,
    {"input": inputs, "extra_args": extra_args},
    None,
    lambda_worker_function_name=lambda_worker_function_name,
)


@patch("aioboto3.client", new_callable=Mock)
def test_default_handler_success(mock_invoke):

    expected_result = setup_success_mock_responses(mock_invoke, inputs)
    result = call_handler()

    assert result == expected_result


@patch("aioboto3.client", new_callable=Mock)
def test_default_handler_client_failure(mock_invoke):
    expected_results = setup_first_failure_mock_responses(mock_invoke, inputs)
    result = call_handler()

    assert result[0]["exception"] == "ClientError"
    assert result[1:] == expected_results


@patch(
    "werkit.aws_lambda.parallel.call_worker_service",
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
)
@patch("aioboto3.client", new_callable=Mock)
def test_default_handler_timeout_failure(mock_invoke):
    setup_success_mock_responses(mock_invoke, inputs)
    results = call_handler(timeout=1)
    assert all([r["exception"] == "TimeoutError" for r in results])
