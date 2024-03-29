import typing as t
import pytest

from . import DefaultStateManagerProtocol
from .testing_examples import MyComputeProcess


def test_bound_property_for_input() -> None:
    compute_process = MyComputeProcess()
    t.cast(DefaultStateManagerProtocol, compute_process).state_manager.set(a=1)
    assert compute_process.a == 1


def test_bound_property_raises_exception_for_unset_input() -> None:
    compute_process = MyComputeProcess()
    with pytest.raises(KeyError, match="Input has not been set: a"):
        compute_process.a


def test_bound_property_for_inner_nodes() -> None:
    compute_process = MyComputeProcess()
    t.cast(DefaultStateManagerProtocol, compute_process).state_manager.set(a=1)
    assert compute_process.i == 1

    compute_process = MyComputeProcess()
    t.cast(DefaultStateManagerProtocol, compute_process).state_manager.set(a=1, b=2)
    assert compute_process.r == 3
