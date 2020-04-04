import time
import os

LAMBDA_WORKER_DELAY = 'LAMBDA_WORKER_DELAY'
env_lambda_worker_delay = int(os.environ[LAMBDA_WORKER_DELAY]) if LAMBDA_WORKER_DELAY in os.environ else 0

def handler(event, context):
    time.sleep(env_lambda_worker_delay)   #wait 3 seconds
    return event['input'] + sum(event['extra_args'])

