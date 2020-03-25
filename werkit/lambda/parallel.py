import boto3
import json
import asyncio
import os

client = boto3.client('lambda')

LAMBDA_WORKER_FUNCTION_NAME = 'LAMBDA_WORKER_FUNCTION_NAME'

if LAMBDA_WORKER_FUNCTION_NAME not in os.environ:
    raise Error(f'Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined to use s3_upload_handler')

lambda_worker_function_name = os.environ[LAMBDA_WORKER_FUNCTION_NAME]

#TODO: how to handle errors
async def call_worker_service(y):
    response = client.invoke(
        FunctionName=lambda_worker_function_name,
        Payload=json.dumps(y)
    )
    return json.load(response['Payload'])

async def synchronous_map_on_lambda(x):
    #TODO: deal with object arg
    coroutines = [call_worker_service(y) for y in x] 
    completed, pending  = await asyncio.wait(coroutines)
    return [r.result() for r in completed]

