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
    def work(input: t.Any) -> t.Any:
        return EXAMPLE_RESULT

    manager = create_manager()
    output_message = manager.work(work, should_send=False, should_return=True)

    assert output_message == {
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

    def work(input: t.Any) -> t.Any:
        time.sleep(0.35)
        return EXAMPLE_RESULT

    manager = create_manager()
    output_message = manager.work(work, should_send=False, should_return=True)

    assert output_message["duration_seconds"] >= 0.35
    assert output_message["duration_seconds"] < 0.4


@freeze_time("2019-12-31")
def test_manager_serializes_error() -> None:
    def work(input: t.Any) -> t.Any:
        raise ValueError("No good!")

    manager = create_manager()
    output_message = manager.work(work, should_send=False, should_return=True)

    assert output_message["error"][-1] == "ValueError: No good!\n"
    del output_message["error"]

    assert output_message == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_manager_with_handle_exceptions_false_passes_error() -> None:
    def work(input: t.Any) -> t.Any:
        raise ValueError("No good!")

    manager = create_manager(handle_exceptions=False)
    with pytest.raises(ValueError, match=r"No good!$"):
        manager.work(work, should_send=False, should_return=True)


@freeze_time("2019-12-31")
def test_manager_serializes_synthetic_error() -> None:
    from ._synthetic_error import SyntheticError

    def work_inner(input: t.Any) -> t.Any:
        raise ValueError("No good!")

    def work(input: t.Any) -> t.Any:
        output_message = create_manager().work(
            work_inner, should_send=False, should_return=True
        )
        assert output_message["success"] is False
        raise SyntheticError(output_message)

    manager = create_manager()
    output_message = manager.work(work, should_send=False, should_return=True)

    assert output_message["error"][-1] == "ValueError: No good!\n"
    del output_message["error"]

    assert output_message == {
        "message_key": EXAMPLE_MESSAGE_KEY,
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": EXAMPLE_RUNTIME_INFO,
    }


def test_manager_passes_keyboard_interrupt() -> None:
    def work(input: t.Any) -> t.Any:
        raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        create_manager().work(work, should_send=False, should_return=True)


def test_manager_passes_value_error_and_skips_body_when_input_message_has_no_message_key_and_fails_validation() -> (
    None
):
    from unittest.mock import Mock

    mock = Mock()

    def work(input: t.Any) -> t.Any:
        mock()

    with pytest.raises(
        ValueError, match="Input message is missing `message_key` property"
    ):
        create_manager(schema=schema, input_message=math.pi).work(
            work, should_send=False, should_return=True
        )

    mock.assert_not_called()


def test_manager_passes_value_error_and_skips_work_fn_when_input_message_has_no_message_key_and_passes_validation() -> (
    None
):
    from unittest.mock import Mock

    schema = Schema.load_relative_to_file(
        __file__,
        ["generated", "manager_testing.schema.json"],
        input_message_ref="#/definitions/Anything",
    )

    mock = Mock()

    def work(input: t.Any) -> t.Any:
        mock()

    with pytest.raises(
        ValueError, match="Input message is missing `message_key` property"
    ):
        create_manager(schema=schema, input_message=math.pi).work(
            work, should_send=False, should_return=True
        )

    mock.assert_not_called()


def test_manager_skips_work_fn_when_input_message_has_message_key_but_fails_validation() -> (
    None
):
    from unittest.mock import Mock

    mock = Mock()

    def work(input: t.Any) -> t.Any:
        mock()

    create_manager(input_message={"message_key": None}).work(
        work, should_send=False, should_return=True
    )

    mock.assert_not_called()


def test_verbose_success(capfd: pytest.CaptureFixture[str]) -> None:
    def work(input: t.Any) -> t.Any:
        return EXAMPLE_RESULT

    create_manager(verbose=True).work(work, should_send=False, should_return=True)

    out, err = capfd.readouterr()
    assert err == "Completed in 0.0 sec\n"


def test_verbose_error(capfd: pytest.CaptureFixture[str]) -> None:
    def work(input: t.Any) -> t.Any:
        raise ValueError()

    create_manager(verbose=True).work(work, should_send=False, should_return=True)

    out, err = capfd.readouterr()
    assert err == "Errored in 0.0 sec\n"
