import pytest
from . import Manager


def test_manage_execution_serializes_result():
    with Manager() as manager:
        manager.result = 2

    assert manager.serialized_result == {
        "success": True,
        "result": 2,
        "error": None,
        "error_origin": None,
        "duration_seconds": 0,
    }

def test_time_precision():
    import time

    with Manager() as manager:
        time.sleep(0.35)
        manager.result = 2

    assert manager.serialized_result["duration_seconds"] >= 0.35
    assert manager.serialized_result["duration_seconds"] < 0.4

def test_manage_execution_serializes_error():
    with Manager() as manager:
        raise ValueError()

    assert manager.serialized_result["error"][-1] == "ValueError\n"
    del manager.serialized_result["error"]

    assert manager.serialized_result == {
        "success": False,
        "result": None,
        "error_origin": "compute",
        "duration_seconds": 0,
    }


def test_manage_execution_passes_error():
    with pytest.raises(ValueError):
        with Manager(handle_exceptions=False) as manager:
            raise ValueError()


def test_manage_execution_passes_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt):
        with Manager() as manager:
            raise KeyboardInterrupt()


def test_verbose(capfd):
    with Manager(verbose=True) as manager:
        manager.result = 2

    out, err = capfd.readouterr()
    assert err == "Completed in 0.0 sec\n"
