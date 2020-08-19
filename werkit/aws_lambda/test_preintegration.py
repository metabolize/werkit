from .test_worker.service import handler
from ..schema import validate_result


def test_test_service():
    result = handler(event={"input": 1, "extra_args": [2, 3]}, context=None)
    validate_result(result)
