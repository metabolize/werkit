import numbers

from . import DependencyGraph
from .testing_examples import (
    EXPECTED_INPUTS,
    EXPECTED_INTERMEDIATES,
    EXPECTED_OUTPUT,
    EXPECTED_SERIALIZED_DEPENDENCY_GRAPH,
    MyComputeProcess,
)


def test_dependency_graph_collects_dependencies() -> None:
    dependency_graph = DependencyGraph.from_class(MyComputeProcess)

    assert set(dependency_graph.inputs.keys()) == set(EXPECTED_INPUTS)
    assert set(dependency_graph.intermediates.keys()) == set(EXPECTED_INTERMEDIATES)
    assert set(dependency_graph.outputs.keys()) == set([EXPECTED_OUTPUT])


def test_dependency_graph_dependencies_have_correct_types() -> None:
    dependency_graph = DependencyGraph.from_class(MyComputeProcess)

    for name in EXPECTED_INPUTS:
        assert dependency_graph.inputs[name].value_type is int
    for name in EXPECTED_INTERMEDIATES:
        assert dependency_graph.intermediates[name].value_type is int
    assert dependency_graph.outputs[EXPECTED_OUTPUT].value_type is int


def test_dependency_graph_deserialize():
    dependency_graph = DependencyGraph.deserialize(EXPECTED_SERIALIZED_DEPENDENCY_GRAPH)

    for name in EXPECTED_INPUTS:
        assert dependency_graph.inputs[name].value_type is numbers.Number
    for name in EXPECTED_INTERMEDIATES:
        assert dependency_graph.intermediates[name].value_type is numbers.Number
    assert dependency_graph.outputs[EXPECTED_OUTPUT].value_type is numbers.Number


def test_dependency_graph_serializes() -> None:
    dependency_graph = DependencyGraph.from_class(MyComputeProcess)

    assert dependency_graph.serialize() == EXPECTED_SERIALIZED_DEPENDENCY_GRAPH


def test_dependency_graph_serialization_matches_schema() -> None:
    from ._dependency_graph import assert_valid_dependency_graph_data

    dependency_graph = DependencyGraph.from_class(MyComputeProcess)
    serialized = dependency_graph.serialize()

    assert_valid_dependency_graph_data(serialized)
