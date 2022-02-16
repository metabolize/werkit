from . import DependencyGraph
from .testing_example import (
    MyComputeProcess,
    EXPECTED_INPUTS,
    EXPECTED_OUTPUT,
    EXPECTED_INTERMEDIATES,
    EXPECTED_SERIALIZED_TREE,
)


def test_dependency_graph_collects_dependencies():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert set(dependency_graph.inputs.keys()) == set(EXPECTED_INPUTS)
    assert set(dependency_graph.intermediates.keys()) == set(EXPECTED_INTERMEDIATES)
    assert set(dependency_graph.outputs.keys()) == set([EXPECTED_OUTPUT])


def test_dependency_graph_dependencies_have_correct_types():
    dependency_graph = DependencyGraph(MyComputeProcess)

    for name in EXPECTED_INPUTS:
        assert dependency_graph.inputs[name]._type == "Number"
    for name in EXPECTED_INTERMEDIATES:
        assert dependency_graph.intermediates[name]._type == "Number"
    assert dependency_graph.outputs[EXPECTED_OUTPUT]._type == "Number"


def test_dependency_graph_serializes():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert dependency_graph.as_native() == EXPECTED_SERIALIZED_TREE
