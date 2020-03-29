def handler(event, context):
    return event['input'] + sum(event['extra_args'])
