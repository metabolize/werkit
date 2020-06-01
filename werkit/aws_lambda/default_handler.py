import asyncio
import os
from botocore.exceptions import ClientError
from .parallel import parallel_map_on_lambda
from ..schema import validate_result, wrap_exception

LAMBDA_WORKER_FUNCTION_NAME = "LAMBDA_WORKER_FUNCTION_NAME"
env_lambda_worker_function_name = os.environ.get(LAMBDA_WORKER_FUNCTION_NAME)

LAMBDA_WORKER_TIMEOUT = "LAMBDA_WORKER_TIMEOUT"
env_lambda_worker_timeout = (
    int(os.environ[LAMBDA_WORKER_TIMEOUT])
    if LAMBDA_WORKER_TIMEOUT in os.environ
    else None
)


def transform_result(result):
    if isinstance(result, ClientError):
        return wrap_exception(exception=result, error_origin="orchestration")
    elif isinstance(result, asyncio.TimeoutError):
        return wrap_exception(exception=result, error_origin="orchestration")
    elif isinstance(result, Exception):
        return wrap_exception(exception=result, error_origin="orchestration")
    else:
        validate_result(result)
        return result


def handler(
    event,
    context,
    lambda_worker_function_name=env_lambda_worker_function_name,
    timeout=env_lambda_worker_timeout or 120,
):
    if not lambda_worker_function_name:
        raise Exception(
            f"Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, "
            + "or default kwArg lambda_worker_function_name must be bound to the handler"
        )
    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        parallel_map_on_lambda(lambda_worker_function_name, timeout, **event)
    )
    return [transform_result(result) for result in results]
