import asyncio
import json
import aioboto3
from botocore.exceptions import ClientError
from harrison import Timer


async def call_worker_service(
    lambda_worker_function_name, extra_args, _input, with_timing=False
):
    async with aioboto3.client("lambda") as lambda_client:
        with Timer(verbose=False) as response_timer:
            response = await lambda_client.invoke(
                FunctionName=lambda_worker_function_name,
                Payload=json.dumps({"input": _input, "extra_args": extra_args}),
            )
        payload = await response["Payload"].read()
        result = json.loads(payload.decode())
        if with_timing:
            result["lambda_roundtrip_seconds"] = response_timer.elapsed_time_s
        return result


async def wait_for(
    timeout, lambda_worker_function_name, extra_args, _input, with_timing=False
):
    try:
        return await asyncio.wait_for(
            call_worker_service(
                lambda_worker_function_name, extra_args, _input, with_timing=with_timing
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
    lambda_worker_function_name, timeout, input, extra_args=[], with_timing=False
):
    coroutines = [
        wait_for(
            timeout=timeout,
            lambda_worker_function_name=lambda_worker_function_name,
            _input=item,
            extra_args=extra_args,
            with_timing=with_timing,
        )
        for item in input
    ]
    return await asyncio.gather(*coroutines, return_exceptions=True)
