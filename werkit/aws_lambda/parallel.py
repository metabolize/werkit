import asyncio
import json
from functools import partial
import aioboto3
from botocore.exceptions import ClientError


async def call_worker_service(lambda_worker_function_name, extra_args, _input):
    async with aioboto3.client("lambda") as lambda_client:
        # tic = time.time()
        response = await lambda_client.invoke(
            FunctionName=lambda_worker_function_name,
            Payload=json.dumps({"input": _input, "extra_args": extra_args}),
        )
        # toc = time.time()
        # print(_input, toc - tic)
        payload = await response["Payload"].read()
        return json.loads(payload.decode())


async def wait_for(timeout, lambda_worker_function_name, extra_args, _input):
    try:
        return await asyncio.wait_for(
            call_worker_service(lambda_worker_function_name, extra_args, _input),
            timeout=timeout,
        )
    except ClientError as ex:
        return ex
    except asyncio.TimeoutError as ex:
        return ex
    except Exception as ex:
        return ex


async def parallel_map_on_lambda(
    lambda_worker_function_name, timeout, input, extra_args=[]
):
    _call_worker_service = partial(
        wait_for, timeout, lambda_worker_function_name, extra_args
    )
    coroutines = list(map(_call_worker_service, input))
    return await asyncio.gather(*coroutines, return_exceptions=True)
