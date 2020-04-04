import pdb
import boto3
import json
import asyncio
import os
from functools import partial
from botocore.exceptions import ClientError

client = boto3.client(
    "lambda",
    region_name=os.environ["AWS_REGION"] if "AWS_REGION" in os.environ else None,
)


async def call_worker_service(lambda_worker_function_name, extra_args, _input):
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None,
        partial(
            client.invoke,
            FunctionName=lambda_worker_function_name,
            Payload=json.dumps({"input": _input, "extra_args": extra_args}),
        ),
    )
    return json.load(response["Payload"])


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
