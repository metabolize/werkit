import asyncio
import datetime
import typing as t
from concurrent.futures import ThreadPoolExecutor
import boto3
from botocore.exceptions import ClientError
from harrison import Timer

if t.TYPE_CHECKING:
    from mypy_boto3_lambda.client import LambdaClient
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef

lambda_client: "LambdaClient" = boto3.client("lambda")
event_loop = asyncio.get_event_loop()


async def call_worker_service(
    worker_lambda_function_name: str,
    _input: dict[str, t.Any],
    event_loop: asyncio.AbstractEventLoop = event_loop,
    executor: t.Optional[ThreadPoolExecutor] = None,
) -> t.Any:
    from missouri import json

    def invoke_lambda() -> "InvocationResponseTypeDef":
        return lambda_client.invoke(
            FunctionName=worker_lambda_function_name, Payload=json.dumps(_input)
        )

    start_timestamp = datetime.datetime.utcnow().timestamp()
    with Timer(verbose=False) as roundtrip_timer:
        response = await event_loop.run_in_executor(executor, invoke_lambda)
        payload = await event_loop.run_in_executor(executor, response["Payload"].read)
    output = json.loads(payload.decode())
    output["orchestrationStartTimestamp"] = start_timestamp
    output["workerRoundtripSeconds"] = roundtrip_timer.elapsed_time_s
    return output


# TODO: This is imported from some utility code which invokes a lambda.
# Generalize this function and move it outside this `orchestrator_lambda`
# module.
async def wait_for(
    _input: dict[str, t.Any],
    timeout: int,
    worker_lambda_function_name: str,
    event_loop: asyncio.AbstractEventLoop = event_loop,
    executor: t.Optional[ThreadPoolExecutor] = None,
) -> t.Any:
    try:
        return await asyncio.wait_for(
            call_worker_service(
                worker_lambda_function_name=worker_lambda_function_name,
                _input=_input,
                event_loop=event_loop,
                executor=executor,
            ),
            timeout=timeout,
        )
    except ClientError as ex:
        return ex
    except asyncio.TimeoutError as ex:
        return ex
    except Exception as ex:
        return ex


async def parallel_map_on_lambda(
    message_key: t.Any,
    item_property_name: str,
    item_collection: dict[str, dict[str, t.Any]],
    common_input: dict[str, t.Any],
    worker_lambda_function_name: str,
    timeout: int,
    event_loop: asyncio.AbstractEventLoop = event_loop,
    executor: t.Optional[ThreadPoolExecutor] = None,
) -> list[t.Any]:
    coroutines = [
        wait_for(
            _input={
                **common_input,
                "message_key": message_key,
                "itemKey": item_key,
                item_property_name: item,
            },
            worker_lambda_function_name=worker_lambda_function_name,
            timeout=timeout,
            event_loop=event_loop,
            executor=executor,
        )
        for item_key, item in item_collection.items()
    ]
    return await asyncio.gather(*coroutines, return_exceptions=True)
