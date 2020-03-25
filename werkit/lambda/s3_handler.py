import os
import boto3
import asyncio
import json
from .default_handler import handler as default_handler

S3_INPUT_BUCKET = 'S3_INPUT_BUCKET'
S3_OUTPUT_BUCKET = 'S3_OUTPUT_BUCKET'

for k in [S3_INPUT_BUCKET, S3_OUTPUT_BUCKET]:
    if k not in os.environ:
        raise Error(f'Environment variable {k} must be defined to use s3_upload_handler')


s3_input_bucket = os.environ[S3_INPUT_BUCKET]
s3_output_bucket = os.environ[S3_OUTPUT_BUCKET]

s3 = boto3.resource('s3')

def handler(event, context):
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    o = s3.Object(s3_input_bucket, s3_key)   #TODO: can we the bucket from the s3 object?
    x = json.load(o.get()['Body'])
    result = default_handler(x, context)
    o2 = s3.Object(s3_output_bucket, s3_key) #TODO: parameterize handling of result
    o2.put(Body=json.dumps(result))
    return result 
