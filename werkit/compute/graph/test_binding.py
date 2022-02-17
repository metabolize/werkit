import pytest
from .testing_examples import MyComputeProcess


def test_bound_can_access_input_using_property_access():
    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1)
    assert compute_process.a == 1


def test_bound_raises_exception_for_unset_input():
    compute_process = MyComputeProcess()
    with pytest.raises(KeyError, match="Input has not been set: a"):
        compute_process.a


def test_bound_can_access_node_using_property_access():
    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1)
    assert compute_process.i == 1

    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1, b=2)
    assert compute_process.r == 3
