import pytest
from .testing_example import MyComputeProcess


def test_state_manager_initial_state_is_empty():
    assert MyComputeProcess().state_manager.store == {}


def test_state_manager_seed():
    state_manager = MyComputeProcess().state_manager

    state_manager.seed(a=3)
    assert state_manager.store == {"a": 3}

    state_manager.seed(a=4, b=5)
    assert state_manager.store == {"a": 4, "b": 5}

    with pytest.raises(KeyError, match=r"Unknown key: i"):
        state_manager.seed(i=5)

    with pytest.raises(KeyError, match=r"Unknown keys: x, y"):
        state_manager.seed(x=5, y=5)
