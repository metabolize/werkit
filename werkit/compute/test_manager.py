import datetime
import math
from freezegun import freeze_time
import pytest
from werkit.compute import Manager, Schema

EXAMPLE_RUNTIME_INFO = {"foo": "bar"}
EXAMPLE_MESSAGE_KEY = {"someParameters": ["just", "a", "message", "key", "nbd"]}
EXAMPLE_INPUT_MESSAGE = {
    "label": "hey",
    "message": "there",
    "message_key": {"someParameters": ["just", "a", "message", "key", "nbd"]},
}
EXAMPLE_RESULT = {"someString": "this is a string!", "someNumber": math.pi}

schema = Schema.load_relative_to_file(
    __file__,
    ["test_schema", "generated", "schema.json"],
    request_ref="#/definitions/AnyInputMessage",
    result_ref="#/definitions/Output",
    serialized_result_ref="#/definitions/AnyOutputMessage",
)


def create_manager(
    input_message=EXAMPLE_INPUT_MESSAGE,
    schema=schema,
    runtime_info=EXAMPLE_RUNTIME_INFO,
    **kwargs
):
    return Manager(
        input_message=input_message, schema=schema, runtime_info=runtime_info, **kwargs
    )


@freeze_time("2019-12-31")
def test_manager_serializes_result():
    with create_manager() as manager:
        manager.result = EXAMPLE_RESULT

    assert manager.serialized_result == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": True,
        "result": EXAMPLE_RESULT,
        "error": None,
        "error_origin": None,
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_time_precision():
    import time

    with create_manager() as manager:
        time.sleep(0.35)
        manager.result = EXAMPLE_RESULT

    assert manager.serialized_result["duration_seconds"] >= 0.35
    assert manager.serialized_result["duration_seconds"] < 0.4


@freeze_time("2019-12-31")
def test_manager_serializes_error():
    with create_manager() as manager:
        raise ValueError()

    assert manager.serialized_result["error"][-1] == "ValueError\n"
    del manager.serialized_result["error"]

    assert manager.serialized_result == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


@freeze_time("2019-12-31")
def test_manager_serializes_expected_error_when_result_not_set():
    with create_manager() as manager:
        pass

    assert (
        manager.serialized_result["error"][-1]
        == "AttributeError: 'result' was not set on the 'Manager' instance\n"
    )
    del manager.serialized_result["error"]

    assert manager.serialized_result == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_manager_with_handle_exceptions_false_passes_error():
    with pytest.raises(ValueError):
        with create_manager(handle_exceptions=False):
            raise ValueError()


def test_manager_passes_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt):
        with create_manager():
            raise KeyboardInterrupt()


def test_manager_passes_value_error_when_no_message_key_present():
    with pytest.raises(
        ValueError, match="Input message is missing `message_key` property"
    ):
        with create_manager(input_message=math.pi) as manager:
            manager.result = EXAMPLE_RESULT


def test_verbose_success(capfd):
    with create_manager(verbose=True) as manager:
        manager.result = EXAMPLE_RESULT

    out, err = capfd.readouterr()
    assert err == "Completed in 0.0 sec\n"


def test_verbose_error(capfd):
    with create_manager(verbose=True):
        raise ValueError()

    out, err = capfd.readouterr()
    assert err == "Errored in 0.0 sec\n"
