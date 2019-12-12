import pytest
from . import Manager


def test_manage_execution_serializes_result():
    with Manager() as manager:
        manager.result = 2

    assert manager.serialized_result == {
        "success": True,
        "result": 2,
        "error": None,
        "duration_seconds": 0,
    }


def test_manage_execution_serializes_error():
    with Manager() as manager:
        raise ValueError()

    assert manager.serialized_result["error"][-1] == "ValueError\n"
    del manager.serialized_result["error"]

    assert manager.serialized_result == {
        "success": False,
        "result": None,
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
    assert out == "Completed in 0 sec\n"
