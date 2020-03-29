import pdb
import boto3
import json
import asyncio
import os
from functools import partial

client = boto3.client('lambda')

async def call_worker_service(lambda_worker_function_name, extra_args, _input):
    response = client.invoke(
        FunctionName=lambda_worker_function_name,
        Payload=json.dumps({'input': _input, 'extra_args': extra_args})
    )
    return json.load(response['Payload'])

async def parallel_map_on_lambda(lambda_worker_function_name, input, extra_args=[]):
    _call_worker_service = partial(call_worker_service, lambda_worker_function_name, extra_args)
    coroutines = list(map(_call_worker_service, input))
    responses = await asyncio.gather(*coroutines, return_exceptions=True)
    return responses

