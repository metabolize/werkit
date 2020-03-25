zip function.zip -r werkit venv/lib/python3.7/site-packages/*
aws lambda create-function --function-name test_werkit --runtime python3.7  --role arn:aws:iam::139234625917:role/purl-lambda-s3-poc --handler werkit.lambda.s3_handler.handler --zip-file fileb://function.zip --environment 'Variables={S3_INPUT_BUCKET=testtape,S3_OUTPUT_BUCKET=testtape-output,LAMBDA_WORKER_FUNCTION_NAME=worker_service2}'
#aws lambda invoke --function-name werkit.lambda.s3_handler --payload '{"x": 1}' test.json
