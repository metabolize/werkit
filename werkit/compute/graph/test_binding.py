import pytest
from .testing_examples import MyComputeProcess


def test_bound_property_for_input():
    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1)
    assert compute_process.a == 1


def test_bound_property_raises_exception_for_unset_input():
    compute_process = MyComputeProcess()
    with pytest.raises(KeyError, match="Input has not been set: a"):
        compute_process.a


def test_bound_property_for_inner_nodes():
    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1)
    assert compute_process.i == 1

    compute_process = MyComputeProcess()
    compute_process.state_manager.set(a=1, b=2)
    assert compute_process.r == 3
