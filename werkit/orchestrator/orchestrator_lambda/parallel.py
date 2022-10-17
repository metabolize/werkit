import asyncio
import datetime
import json
import boto3
from botocore.exceptions import ClientError
from harrison import Timer


lambda_client = boto3.client("lambda")
event_loop = asyncio.get_event_loop()


async def call_worker_service(
    worker_lambda_function_name,
    _input,
    event_loop=event_loop,
    executor=None,
):
    def invoke_lambda():
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
    _input,
    timeout,
    worker_lambda_function_name,
    event_loop=event_loop,
    executor=None,
):
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
    message_key,
    item_property_name,
    item_collection,
    common_input,
    worker_lambda_function_name,
    timeout,
    event_loop=event_loop,
    executor=None,
):
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
