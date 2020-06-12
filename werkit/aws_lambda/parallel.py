import asyncio
import datetime
import json
from functools import partial
import boto3
from botocore.exceptions import ClientError
from harrison import Timer


lambda_client = boto3.client("lambda")
event_loop = asyncio.get_event_loop()


async def call_worker_service(
    lambda_worker_function_name,
    extra_args,
    _input,
    with_timing=True,
    event_loop=event_loop,
    executor=None,
):
    invocation_start_timestamp = datetime.datetime.utcnow().timestamp()
    invoke = partial(
        lambda_client.invoke,
        FunctionName=lambda_worker_function_name,
        Payload=json.dumps({"input": _input, "extra_args": extra_args}),
    )
    with Timer(verbose=False) as response_timer:
        response = await event_loop.run_in_executor(executor, invoke)
        payload = await event_loop.run_in_executor(executor, response["Payload"].read)
    result = json.loads(payload.decode())
    if with_timing:
        result["invocation_start_timestamp"] = invocation_start_timestamp
        result["lambda_roundtrip_seconds"] = response_timer.elapsed_time_s
    return result


async def wait_for(
    timeout,
    lambda_worker_function_name,
    extra_args,
    _input,
    with_timing=True,
    event_loop=event_loop,
    executor=None,
):
    try:
        return await asyncio.wait_for(
            call_worker_service(
                lambda_worker_function_name,
                extra_args,
                _input,
                event_loop=event_loop,
                executor=executor,
                with_timing=with_timing,
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
    lambda_worker_function_name,
    timeout,
    input,
    extra_args=[],
    with_timing=True,
    event_loop=event_loop,
    executor=None,
):
    coroutines = [
        wait_for(
            timeout=timeout,
            lambda_worker_function_name=lambda_worker_function_name,
            _input=item,
            extra_args=extra_args,
            with_timing=with_timing,
            event_loop=event_loop,
            executor=executor,
        )
        for item in input
    ]
    return await asyncio.gather(*coroutines, return_exceptions=True)
