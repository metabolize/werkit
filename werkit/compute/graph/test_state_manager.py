from artifax.exceptions import UnresolvedDependencyError
import pytest
from .testing_examples import (
    MyComputeProcess,
    MyComputeProcessSubclass,
    MyComputeProcessWithCustomType,
    MyRaisingComputeProcess,
    MyWronglyTypedComputeProcess,
)


def test_state_manager_initial_state_is_empty() -> None:
    assert MyComputeProcess().state_manager.store == {}


def test_state_manager_set() -> None:
    state_manager = MyComputeProcess().state_manager

    state_manager.set(a=3)
    assert state_manager.store == {"a": 3}

    state_manager.set(a=4, b=5)
    assert state_manager.store == {"a": 4, "b": 5}

    state_manager.set(i=6)
    assert state_manager.store == {"a": 4, "b": 5, "i": 6}

    with pytest.raises(KeyError, match=r"Unknown keys: also_bogus, bogus"):
        state_manager.set(bogus=5, also_bogus=5)


def test_state_manager_deserialize() -> None:
    state_manager = MyComputeProcess().state_manager

    state_manager.deserialize(a=3)
    assert state_manager.store == {"a": 3}

    state_manager.deserialize(a=4, b=5)
    assert state_manager.store == {"a": 4, "b": 5}

    state_manager.deserialize(i=6)
    assert state_manager.store == {"a": 4, "b": 5, "i": 6}

    with pytest.raises(KeyError, match=r"Unknown keys: also_bogus, bogus"):
        state_manager.deserialize(bogus=5, also_bogus=5)


def test_state_manager_evaluate() -> None:
    state_manager = MyComputeProcess().state_manager

    state_manager.set(a=1, b=2)
    state_manager.evaluate()
    assert state_manager.store == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}

    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    state_manager.evaluate(targets=["i"])
    assert state_manager.store == {"a": 1, "i": 1}


def test_state_manager_evaluate_on_subclass() -> None:
    state_manager = MyComputeProcessSubclass().state_manager
    state_manager.set(a=1, b=2)
    state_manager.evaluate()
    assert state_manager.store == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}


def test_state_manager_evaluate_unknown_key() -> None:
    with pytest.raises(KeyError, match=r"Unknown key: bogus"):
        MyComputeProcess().state_manager.evaluate(targets=["bogus"])


def test_state_manager_evaluate_with_missing_dependencies() -> None:
    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    with pytest.raises(UnresolvedDependencyError):
        state_manager.evaluate()

    with pytest.raises(UnresolvedDependencyError):
        MyComputeProcess().state_manager.evaluate()


def test_state_manager_evaluate_exceptions() -> None:
    state_manager = MyRaisingComputeProcess().state_manager
    state_manager.set(a=1, b=1)
    # TODO: We want computation to continue and errors to propagate.
    with pytest.raises(ValueError):
        state_manager.evaluate()


def test_state_manager_set_type_mismatch() -> None:
    state_manager = MyComputeProcess().state_manager
    with pytest.raises(ValueError, match="a should be type int, not bool"):
        state_manager.set(a=False)


def test_state_manager_evaluate_type_mismatch() -> None:
    state_manager = MyWronglyTypedComputeProcess().state_manager
    state_manager.set(a=1, b=1)
    with pytest.raises(ValueError, match="s should be type int, not bool"):
        state_manager.evaluate()


def test_state_manager_serializes() -> None:
    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1, b=2)
    # TODO: These should be wrapped in the werkit result format.
    assert state_manager.serialize() == {"a": 1, "b": 2, "i": 1, "j": 2, "r": 3}
    assert state_manager.serialize(targets=["r"]) == {"r": 3}

    state_manager = MyComputeProcess().state_manager
    state_manager.set(a=1)
    # TODO: These should be wrapped in the werkit result format.
    assert state_manager.serialize(targets=["i"]) == {"i": 1}


def test_state_manager_serializes_exceptions() -> None:
    """
    TODO
    """


# TODO: Provide a way to serialize only the properties which have been computed.


def test_state_manager_with_custom_type() -> None:
    state_manager = MyComputeProcessWithCustomType().state_manager
    state_manager.set(a=1, b=2)
    state_manager.evaluate()

    thing = state_manager.store["thing"]
    assert thing.title == "Example title"
    assert thing.description == "Example description"
    assert thing.count == 25

    assert state_manager.store["other_thing"] == (1.52, 2.52, 3.52)


def test_state_manager_deserializes_custom_type() -> None:
    state_manager = MyComputeProcessWithCustomType().state_manager

    state_manager.deserialize(
        thing={"title": "New title", "description": "New description", "count": 5},
        other_thing=[3, 4, 5],
    )

    thing = state_manager.store["thing"]
    assert thing.title == "New title"
    assert thing.description == "New description"
    assert thing.count == 5

    assert state_manager.store["other_thing"] == (3, 4, 5)


def test_state_manager_serializes_custom_type() -> None:
    state_manager = MyComputeProcessWithCustomType().state_manager
    state_manager.set(a=1, b=2)
    state_manager.evaluate()

    serialized = state_manager.serialize()

    assert serialized["thing"] == {
        "title": "Example title",
        "description": "Example description",
        "count": 25,
    }
    assert serialized["other_thing"] == [1.52, 2.52, 3.52]
