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


def validate_result(result):
    """
    Validate that the result matches the schema for `werkit.Manager`.
    """
    expected_keys = ["success", "result", "error", "error_origin", "duration_seconds"]
    result_keys = result.keys()
    missing_keys = [k for k in expected_keys if k not in result_keys]
    if len(missing_keys) > 0:
        raise ValueError(
            f"Lambda result contained keys {result_keys.join(',')}, missing {missing_keys.join(',')}"
        )
    if not isinstance(result["success"], bool):
        raise ValueError(
            f"Expected result[\"success\"] to be a bool, got {result['success']}"
        )
    allowed_error_origins = ["compute", "system", "orchestration"]
    if result["error_origin"] not in [None] + allowed_error_origins:
        raise ValueError(
            f"Expected result[\"error_origin\"] to be {allowed_error_origins.join(',')}, or `None`"
        )


def transform_result(result):
    if isinstance(result, ClientError):
        return wrap_exception(exception=result, error_origin="orchestration")
    elif isinstance(result, asyncio.TimeoutError):
        return wrap_exception(exception=result, error_origin="orchestration")
    elif isinstance(result, Exception):
        return wrap_exception(exception=result, error_origin="orchestration")
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
            f"Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, "
            + "or default kwArg lambda_worker_function_name must be bound to the handler"
        )
    event_loop = asyncio.get_event_loop()
    results = event_loop.run_until_complete(
        parallel_map_on_lambda(lambda_worker_function_name, timeout, **event)
    )
    return [transform_result(result) for result in results]
