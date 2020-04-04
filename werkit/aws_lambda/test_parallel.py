import pytest
import pdb
import asyncio
import json

import werkit.aws_lambda.parallel
from botocore.exceptions import ClientError

from unittest.mock import patch
from functools import partial

import io

from werkit.aws_lambda.test_worker.service import handler as worker_handler

from werkit.aws_lambda.test_util import (
    input,
    extra_args,
    lambda_worker_function_name,
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
    setup_first_failure_mock_responses,
    setup_success_mock_responses,
    setup_mock_success_response,
    setup_mock_failure_response,
    init,
    default_timeout,
)


def test_call_worker_service_success():
    # test that we expect to get a successful response out
    stubber = init()

    expected_result = []
    _input = input[0]
    setup_mock_success_response(stubber, expected_result, _input)
    expected_output_payload = expected_result[0]
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.call_worker_service(
            lambda_worker_function_name, extra_args, _input
        )
    )

    assert result == expected_output_payload


# test that we expect to get a client error
def test_call_worker_service_failure():
    stubber = init()
    _input = input[0]
    setup_mock_failure_response(stubber, _input)
    stubber.activate()

    event_loop = asyncio.get_event_loop()
    with pytest.raises(ClientError):
        event_loop.run_until_complete(
            werkit.aws_lambda.parallel.call_worker_service(
                lambda_worker_function_name, extra_args, _input
            )
        )


def test_parallel_map_on_lambda_success():
    expected_result = setup_success_mock_responses()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, default_timeout, input, extra_args
        )
    )

    assert result == expected_result


def test_parallel_map_on_lambda_client_failure():
    expected_results = setup_first_failure_mock_responses()

    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, default_timeout, input, extra_args
        )
    )

    assert isinstance(result[0], ClientError)
    assert result[1:] == expected_results


@patch(
    "werkit.aws_lambda.parallel.call_worker_service",
    parallel_map_on_lambda_timeout_failure_call_worker_service_mock,
)
def test_parallel_map_on_lambda_timeout_failure():
    setup_success_mock_responses()
    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        werkit.aws_lambda.parallel.parallel_map_on_lambda(
            lambda_worker_function_name, 1, input, extra_args
        )
    )

    assert all([isinstance(r, asyncio.TimeoutError) for r in results])
