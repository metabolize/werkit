from .test_worker.service import handler

# from ..compute._serialization import validate_result


def test_test_service():
    handler(event={"input": 1, "extra_args": [2, 3]}, context=None)
    # result = handler(event={"input": 1, "extra_args": [2, 3]}, context=None)
    # validate_result(result)
