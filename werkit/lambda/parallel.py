import boto3
import json
import asyncio
import os

client = boto3.client('lambda')

LAMBDA_WORKER_FUNCTION_NAME = 'LAMBDA_WORKER_FUNCTION_NAME'

if LAMBDA_WORKER_FUNCTION_NAME not in os.environ:
    raise Error(f'Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined to use s3_upload_handler')

lambda_worker_function_name = os.environ[LAMBDA_WORKER_FUNCTION_NAME]

async def call_worker_service(input, extra_args):
    response = client.invoke(
        FunctionName=lambda_worker_function_name,
        Payload=json.dumps({'input': input, 'extra_args': extra_args})
    )
    return json.load(response['Payload'])

async def parallel_map_on_lambda(input, extra_args=[]):
    coroutines = [call_worker_service(y, extra_args) for y in input] 
    responses = await asyncio.gather(*coroutines)
    return responses

