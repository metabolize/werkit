import pytest
import pdb
import asyncio
import json

import werkit.aws_lambda.parallel
from botocore.exceptions import ClientError

from functools import partial

import io

from werkit.aws_lambda.test_worker.service import handler as worker_handler

from werkit.aws_lambda.test_util import (
    inputs,
    extra_args,
    lambda_worker_function_name,
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
    setup_first_failure_mock_responses,
    setup_success_mock_responses,
    setup_mock_failure_response,
    default_timeout,
)

from asynctest import Mock, patch


@patch("aioboto3.client", new_callable=Mock)
def test_call_worker_service_success(mock_invoke):
    _input = inputs[0]

    expected_result = setup_success_mock_responses(mock_invoke, [_input])
    expected_output_payload = expected_result[0]

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.call_worker_service(
            lambda_worker_function_name, extra_args, _input
        )
    )

    assert result == expected_output_payload


# test that we expect to get a client error
@patch("aioboto3.client", new_callable=Mock)
def test_call_worker_service_failure(mock_invoke):
    _input = inputs[0]
    setup_mock_failure_response(mock_invoke, _input)

    event_loop = asyncio.get_event_loop()
    with pytest.raises(ClientError):
        result = event_loop.run_until_complete(
            werkit.aws_lambda.parallel.call_worker_service(
                lambda_worker_function_name, extra_args, _input
            )
        )
        print(result)


@patch("aioboto3.client", new_callable=Mock)
def test_parallel_map_on_lambda_success(mock_invoke):
    expected_result = setup_success_mock_responses(mock_invoke, inputs)

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, default_timeout, inputs, extra_args
        )
    )

    assert result == expected_result


@patch("aioboto3.client", new_callable=Mock)
def test_parallel_map_on_lambda_client_failure(mock_invoke):
    expected_results = setup_first_failure_mock_responses(mock_invoke, inputs)

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, default_timeout, inputs, extra_args
        )
    )

    assert isinstance(result[0], ClientError)
    assert result[1:] == expected_results


@patch(
    "werkit.aws_lambda.parallel.call_worker_service",
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
)
@patch("aioboto3.client", new_callable=Mock)
def test_parallel_map_on_lambda_timeout_failure(mock_invoke):
    setup_success_mock_responses(mock_invoke, inputs)
    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, 1, inputs, extra_args
        )
    )

    assert all([isinstance(r, asyncio.TimeoutError) for r in results])
