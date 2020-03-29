import os
import boto3
import asyncio
from .parallel import parallel_map_on_lambda

def handler(event, context):
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(parallel_map_on_lambda(**event))
    return result 
