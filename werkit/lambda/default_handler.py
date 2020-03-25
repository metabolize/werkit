import os
import boto3
import asyncio
from .parallel import synchronous_map_on_lambda

def handler(event, context):
    #TODO: deal with object arg
    assert isinstance(event, list)
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(synchronous_map_on_lambda(event))
    return result 
