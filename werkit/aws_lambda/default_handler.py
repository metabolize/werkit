import os
import boto3
import asyncio
from .parallel import parallel_map_on_lambda
from botocore.exceptions import ClientError

LAMBDA_WORKER_FUNCTION_NAME = "LAMBDA_WORKER_FUNCTION_NAME"
env_lambda_worker_function_name = (
    os.environ[LAMBDA_WORKER_FUNCTION_NAME]
    if LAMBDA_WORKER_FUNCTION_NAME in os.environ
    else None
)

LAMBDA_WORKER_TIMEOUT = "LAMBDA_WORKER_TIMEOUT"
env_lambda_worker_timeout = (
    int(os.environ[LAMBDA_WORKER_TIMEOUT])
    if LAMBDA_WORKER_TIMEOUT in os.environ
    else None
)


def map_result(result):
    if isinstance(result, ClientError):
        return {
            "exception": "ClientError",
            "args": result.args,
            "operation_name": result.operation_name,
        }
    elif isinstance(result, asyncio.TimeoutError):
        return {
            "exception": "TimeoutError",
            "args": result.args,
        }
    elif isinstance(result, Exception):
        return {
            "exception": "Exception",
            "args": result.args,
        }
    else:
        return result


def handler(
    event,
    context,
    lambda_worker_function_name=env_lambda_worker_function_name,
    timeout=env_lambda_worker_timeout or 120,
):
    if not lambda_worker_function_name:
        raise Exception(
            f"Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, or default kwArg lambda_worker_function_name must be bound to the handler"
        )
    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        parallel_map_on_lambda(lambda_worker_function_name, timeout, **event)
    )
    return list(map(map_result, results))
