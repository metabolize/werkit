import os
import uuid
from botocore.exceptions import ClientError
import boto3
import pytest
from .s3 import temp_file_on_s3


@pytest.fixture
def test_bucket():
    return os.environ["TEST_BUCKET"]


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
        assert s3_client.get_object(Bucket=test_bucket, Key=target_key)[
            "Body"
        ].read() == bytes(EXAMPLE_CONTENTS, "utf-8")

    # Make sure the key is removed after the context handler is closed
    with pytest.raises(ClientError, match=r"Not Found$"):
        s3_client.head_object(Bucket=test_bucket, Key=target_key)


def test_temp_file_on_s3_with_implicit_key(example_file, test_bucket):
    with temp_file_on_s3(
        local_path=example_file, bucket=test_bucket, verbose=True
    ) as key:
        assert key.startswith("example_")
        assert key.endswith(".txt")
