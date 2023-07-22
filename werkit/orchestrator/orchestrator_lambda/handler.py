import asyncio
import concurrent
import datetime
import os
import typing as t
from botocore.exceptions import ClientError

from werkit.compute import Manager
from .parallel import parallel_map_on_lambda
from .schema import SCHEMA
from ...compute._serialization import serialize_exception

LAMBDA_WORKER_FUNCTION_NAME = "LAMBDA_WORKER_FUNCTION_NAME"
env_worker_lambda_function_name = os.environ.get(LAMBDA_WORKER_FUNCTION_NAME)

LAMBDA_WORKER_TIMEOUT = "LAMBDA_WORKER_TIMEOUT"
env_worker_lambda_timeout = (
    int(os.environ[LAMBDA_WORKER_TIMEOUT])
    if LAMBDA_WORKER_TIMEOUT in os.environ
    else None
)


def transform_result(
    message_key: t.Any, result: t.Any, start_time: datetime.datetime
) -> dict[str, t.Any]:
    if (
        isinstance(result, ClientError)
        or isinstance(result, asyncio.TimeoutError)
        # TODO: Could this be replaced with just the following clause?
        or isinstance(result, Exception)
    ):
        return serialize_exception(
            message_key=message_key,
            exception=result,
            error_origin="orchestration",
            start_time=start_time,
        )
    elif isinstance(result, dict) and "errorMessage" in result:
        # https://docs.aws.amazon.com/lambda/latest/dg/python-exceptions.html
        # Unhandled exception in Lambda, with `errorMessage`, `errorType`, and
        # `stackTrace`.
        return {
            "message_key": message_key,
            "success": False,
            "result": None,
            "error": result["stackTrace"]
            + [f"{result['errorType']}: {result['errorMessage']}"],
            "error_origin": "system",
            "start_time": start_time.astimezone().isoformat(),
            "duration_seconds": -1,
        }
    else:
        return result


# TODO: This handler should have a unit test which uses a stubbed lambda. This
# would dramatically simplify debugging this code.
def handler(
    event: dict[str, t.Any],
    context: dict[str, t.Any],
    worker_lambda_function_name: t.Optional[str] = env_worker_lambda_function_name,
    timeout: int = env_worker_lambda_timeout or 120,
) -> dict[str, t.Any]:
    print("input_message", event)
    with Manager(input_message=event, schema=SCHEMA) as manager:
        if not worker_lambda_function_name:
            raise Exception(
                f"Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, "
                + "or default kwArg lambda_worker_function_name must be bound to the handler"
            )
        item_collection = event["itemCollection"]
        event_loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1023) as executor:
            all_results = event_loop.run_until_complete(
                parallel_map_on_lambda(
                    message_key=manager.message_key,
                    item_property_name=event["itemPropertyName"],
                    item_collection=item_collection,
                    common_input=event["commonInput"],
                    worker_lambda_function_name=worker_lambda_function_name,
                    timeout=timeout,
                    event_loop=event_loop,
                    executor=executor,
                )
            )
            manager.result = dict(
                zip(
                    item_collection.keys(),
                    [
                        transform_result(
                            message_key=manager.message_key,
                            result=result,
                            start_time=manager.start_time,
                        )
                        for result in all_results
                    ],
                )
            )
    return manager.output_message
