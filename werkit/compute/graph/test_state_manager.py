from artifax.exceptions import UnresolvedDependencyError
import pytest
from .testing_examples import (
    MyComputeProcess,
    MyComputeProcessSubclass,
    MyRaisingComputeProcess,
    MyWronglyTypedComputeProcess,
)


def test_state_manager_initial_state_is_empty():
    assert MyComputeProcess().state_manager.store == {}


def test_state_manager_set():
    state_manager = MyComputeProcess().state_manager

    state_manager.set(a=3)
    assert state_manager.store == {"a": 3}

    state_manager.set(a=4, b=5)
    assert state_manager.store == {"a": 4, "b": 5}

    state_manager.set(i=6)
    assert state_manager.store == {"a": 4, "b": 5, "i": 6}

    with pytest.raises(KeyError, match=r"Unknown keys: also_bogus, bogus"):
        state_manager.set(bogus=5, also_bogus=5)


def test_state_manager_evaluate():
    state_manager = MyComputeProcess().state_manager

    state_manager.set(a=1, b=2)
    state_manager.evaluate()
    assert state_manager.store == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}

    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    state_manager.evaluate(targets=["i"])
    assert state_manager.store == {"a": 1, "i": 1}


def test_state_manager_evaluate_on_subclass():
    state_manager = MyComputeProcessSubclass().state_manager
    state_manager.set(a=1, b=2)
    state_manager.evaluate()
    assert state_manager.store == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}


def test_state_manager_evaluate_unknown_key():
    with pytest.raises(KeyError, match=r"Unknown key: bogus"):
        MyComputeProcess().state_manager.evaluate(targets=["bogus"])


def test_state_manager_evaluate_with_missing_dependencies():
    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    with pytest.raises(UnresolvedDependencyError):
        state_manager.evaluate()

    with pytest.raises(UnresolvedDependencyError):
        MyComputeProcess().state_manager.evaluate()


def test_state_manager_evaluate_exceptions():
    state_manager = MyRaisingComputeProcess().state_manager
    state_manager.set(a=1, b=1)
    # TODO: We want computation to continue and errors to propagate.
    with pytest.raises(ValueError):
        state_manager.evaluate()


def test_state_manager_set_type_mismatch():
    state_manager = MyComputeProcess().state_manager
    with pytest.raises(ValueError, match="a should be type int, not bool"):
        state_manager.set(a=False)


def test_state_manager_evaluate_type_mismatch():
    state_manager = MyWronglyTypedComputeProcess().state_manager
    state_manager.set(a=1, b=1)
    with pytest.raises(ValueError, match="s should be type int, not bool"):
        state_manager.evaluate()


def test_state_manager_serialize():
    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1, b=2)
    # TODO: These should be wrapped in the werkit result format.
    assert state_manager.serialize() == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}
    assert state_manager.serialize(targets=["r"]) == {"r": 3}

    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    # TODO: These should be wrapped in the werkit result format.
    assert state_manager.serialize(targets=["i"]) == {"i": 1}


def test_state_manager_serialize_exceptions():
    pass


# TODO: Provide a way to serialize only the properties which have been computed.
