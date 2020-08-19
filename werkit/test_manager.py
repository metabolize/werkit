import datetime
from freezegun import freeze_time
import pytest
from . import Manager


@freeze_time("2019-12-31")
def test_manager_serializes_result():
    runtime_info = {"foo": "bar"}
    with Manager(runtime_info=runtime_info) as manager:
        manager.result = 2

    assert manager.serialized_result == {
        "success": True,
        "result": 2,
        "error": None,
        "error_origin": None,
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": runtime_info,
    }


def test_time_precision():
    import time

    with Manager() as manager:
        time.sleep(0.35)
        manager.result = 2

    assert manager.serialized_result["duration_seconds"] >= 0.35
    assert manager.serialized_result["duration_seconds"] < 0.4


@freeze_time("2019-12-31")
def test_manager_serializes_error():
    runtime_info = {"foo": "bar"}
    with Manager(runtime_info=runtime_info) as manager:
        raise ValueError()

    assert manager.serialized_result["error"][-1] == "ValueError\n"
    del manager.serialized_result["error"]

    assert manager.serialized_result == {
        "success": False,
        "result": None,
        "error_origin": "compute",
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 0,
        "runtime_info": runtime_info,
    }


def test_manager_with_handle_exceptions_passes_error():
    with pytest.raises(ValueError):
        with Manager(handle_exceptions=False):
            raise ValueError()


def test_manager_passes_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt):
        with Manager():
            raise KeyboardInterrupt()


def test_verbose(capfd):
    with Manager(verbose=True) as manager:
        manager.result = 2

    out, err = capfd.readouterr()
    assert err == "Completed in 0.0 sec\n"
