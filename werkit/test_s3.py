import os
import uuid
import boto3
from botocore.exceptions import ClientError
import pytest
from .s3 import temp_file_on_s3, temp_file_on_s3_from_string


@pytest.fixture
def test_bucket():
    return os.environ["INTEGRATION_TEST_BUCKET"]


EXAMPLE_KEY = "example.txt"

EXAMPLE_CONTENTS = """
foo
bar
baz
example
"""


@pytest.fixture
def example_file(tmp_path):
    file = tmp_path / EXAMPLE_KEY
    file.write_text(EXAMPLE_CONTENTS)
    return str(file)


def test_temp_file_on_s3(example_file, test_bucket):
    target_key = f"test_{uuid.uuid4().hex}.txt"

    with temp_file_on_s3(
        local_path=example_file, bucket=test_bucket, key=target_key, verbose=True
    ) as key:
        assert key == target_key
        s3_client = boto3.client("s3")
        response = s3_client.get_object(Bucket=test_bucket, Key=target_key)
        assert response["Body"].read() == bytes(EXAMPLE_CONTENTS, "utf-8")

    # Make sure the key is removed after the context handler is closed
    with pytest.raises(ClientError, match=r"Not Found$"):
        s3_client.head_object(Bucket=test_bucket, Key=target_key)


def test_temp_file_on_s3_with_implicit_key(example_file, test_bucket):
    with temp_file_on_s3(
        local_path=example_file, bucket=test_bucket, verbose=True
    ) as key:
        assert key.startswith("example_")
        assert key.endswith(".txt")


def test_temp_file_on_s3_from_string(test_bucket):
    target_key = f"test_{uuid.uuid4().hex}.txt"

    with temp_file_on_s3_from_string(
        contents=EXAMPLE_CONTENTS, bucket=test_bucket, key=target_key, verbose=True
    ) as key:
        assert key == target_key
        s3_client = boto3.client("s3")
        response = s3_client.get_object(Bucket=test_bucket, Key=target_key)
        assert response["Body"].read() == bytes(EXAMPLE_CONTENTS, "utf-8")

    # Make sure the key is removed after the context handler is closed
    with pytest.raises(ClientError, match=r"Not Found$"):
        s3_client.head_object(Bucket=test_bucket, Key=target_key)


def test_temp_file_on_s3_from_string_with_implicit_key(test_bucket):
    with temp_file_on_s3_from_string(
        contents=EXAMPLE_CONTENTS, bucket=test_bucket, extension=".txt", verbose=True
    ) as key:
        assert key.endswith(".txt")
