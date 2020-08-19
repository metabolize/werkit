import asyncio
import concurrent
import datetime
import os
from botocore.exceptions import ClientError
from harrison import Timer
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


def transform_result(result, start_time):
    if (
        isinstance(result, ClientError)
        or isinstance(result, asyncio.TimeoutError)
        # TODO: Could this be replaced with just the following clause?
        or isinstance(result, Exception)
    ):
        return wrap_exception(
            exception=result, error_origin="orchestration", start_time=start_time
        )
    elif isinstance(result, dict) and "errorMessage" in result:
        # https://docs.aws.amazon.com/lambda/latest/dg/python-exceptions.html
        # Unhandled exception in Lambda, with `errorMessage`, `errorType`, and
        # `stackTrace`.
        return {
            "success": False,
            "result": None,
            "error": result["stackTrace"]
            + [f"{result['errorType']}: {result['errorMessage']}"],
            "error_origin": "system",
            "start_time": start_time.astimezone().isoformat(),
            "duration_seconds": -1,
        }
    else:
        validate_result(result)
        return result


def handler(
    event,
    context,
    lambda_worker_function_name=env_lambda_worker_function_name,
    timeout=env_lambda_worker_timeout or 120,
):
    start_time = datetime.datetime.now()
    start_timestamp = datetime.datetime.utcnow().timestamp()

    with Timer(verbose=False) as response_timer:
        if not lambda_worker_function_name:
            raise Exception(
                f"Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, "
                + "or default kwArg lambda_worker_function_name must be bound to the handler"
            )
        event_loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1023) as executor:
            results = event_loop.run_until_complete(
                parallel_map_on_lambda(
                    lambda_worker_function_name,
                    timeout,
                    event_loop=event_loop,
                    executor=executor,
                    **event,
                )
            )
            results = [
                transform_result(result=result, start_time=start_time)
                for result in results
            ]
    return {
        "results": results,
        "orchestrator_duration_seconds": response_timer.elapsed_time_s,
        "start_timestamp": start_timestamp,
    }
