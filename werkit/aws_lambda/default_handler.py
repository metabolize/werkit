import os
import boto3
import asyncio
from .parallel import parallel_map_on_lambda

LAMBDA_WORKER_FUNCTION_NAME = 'LAMBDA_WORKER_FUNCTION_NAME'
env_lambda_worker_function_name = os.environ[LAMBDA_WORKER_FUNCTION_NAME] if LAMBDA_WORKER_FUNCTION_NAME in os.environ else None

def handler(event, context, lambda_worker_function_name=env_lambda_worker_function_name):
    if not lambda_worker_function_name:
        raise Exception(f'Environment variable {LAMBDA_WORKER_FUNCTION_NAME} must be defined, or default kwArg lambda_worker_function_name must be bound to the handler')
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(parallel_map_on_lambda(lambda_worker_function_name, **event))
    return result 
