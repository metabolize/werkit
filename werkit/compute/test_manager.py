import datetime
import math
import typing as t
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
    ["generated", "manager_testing.schema.json"],
)


def create_manager(
    input_message: t.Any = EXAMPLE_INPUT_MESSAGE,
    schema: Schema = schema,
    runtime_info: t.Any = EXAMPLE_RUNTIME_INFO,
    **kwargs: t.Any
) -> Manager:
    return Manager(
        input_message=input_message, schema=schema, runtime_info=runtime_info, **kwargs
    )


@freeze_time("2019-12-31")
def test_manager_serializes_result() -> None:
    with create_manager() as manager:
        manager.result = EXAMPLE_RESULT

    assert manager.output_message == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": True,
        "result": EXAMPLE_RESULT,
        "error": None,
        "error_origin": None,
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_time_precision() -> None:
    import time

    with create_manager() as manager:
        time.sleep(0.35)
        manager.result = EXAMPLE_RESULT

    assert manager.output_message["duration_seconds"] >= 0.35
    assert manager.output_message["duration_seconds"] < 0.4


@freeze_time("2019-12-31")
def test_manager_serializes_error() -> None:
    with create_manager() as manager:
        raise ValueError()

    assert manager.output_message["error"][-1] == "ValueError\n"
    del manager.output_message["error"]

    assert manager.output_message == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


@freeze_time("2019-12-31")
def test_manager_serializes_expected_error_when_result_not_set() -> None:
    with create_manager() as manager:
        pass

    assert (
        manager.output_message["error"][-1]
        == "AttributeError: 'result' was not set on the 'Manager' instance\n"
    )
    del manager.output_message["error"]

    assert manager.output_message == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_manager_with_handle_exceptions_false_passes_error() -> None:
    with pytest.raises(ValueError):
        with create_manager(handle_exceptions=False):
            raise ValueError()


def test_manager_passes_keyboard_interrupt() -> None:
    with pytest.raises(KeyboardInterrupt):
        with create_manager():
            raise KeyboardInterrupt()


def test_manager_passes_value_error_and_skips_body_when_input_message_has_no_message_key_and_fails_validation() -> (
    None
):
    from unittest.mock import Mock

    mock = Mock()

    with pytest.raises(
        ValueError, match="Input message is missing `message_key` property"
    ):
        with create_manager(schema=schema, input_message=math.pi):
            mock()

    mock.assert_not_called()


def test_manager_passes_value_error_and_skips_body_when_input_message_has_no_message_key_and_passes_validation() -> (
    None
):
    from unittest.mock import Mock

    schema = Schema.load_relative_to_file(
        __file__,
        ["generated", "manager_testing.schema.json"],
        input_message_ref="#/definitions/Anything",
    )
    mock = Mock()

    with pytest.raises(
        ValueError, match="Input message is missing `message_key` property"
    ):
        with create_manager(schema=schema, input_message=math.pi):
            mock()

    mock.assert_not_called()


def test_manager_skips_body_when_input_message_has_message_key_but_fails_validation() -> (
    None
):
    from unittest.mock import Mock

    mock = Mock()

    with create_manager(input_message={"message_key": None}):
        mock()

    mock.assert_not_called()


def test_verbose_success(capfd: pytest.CaptureFixture[str]) -> None:
    with create_manager(verbose=True) as manager:
        manager.result = EXAMPLE_RESULT

    out, err = capfd.readouterr()
    assert err == "Completed in 0.0 sec\n"


def test_verbose_error(capfd: pytest.CaptureFixture[str]) -> None:
    with create_manager(verbose=True):
        raise ValueError()

    out, err = capfd.readouterr()
    assert err == "Errored in 0.0 sec\n"
