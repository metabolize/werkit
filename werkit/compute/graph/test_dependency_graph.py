from . import DependencyGraph
from .testing_examples import (
    MyComputeProcess,
    EXPECTED_INPUTS,
    EXPECTED_OUTPUT,
    EXPECTED_INTERMEDIATES,
    EXPECTED_SERIALIZED_DEPENDENCY_GRAPH,
)


def test_dependency_graph_collects_dependencies():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert set(dependency_graph.inputs.keys()) == set(EXPECTED_INPUTS)
    assert set(dependency_graph.intermediates.keys()) == set(EXPECTED_INTERMEDIATES)
    assert set(dependency_graph.outputs.keys()) == set([EXPECTED_OUTPUT])


def test_dependency_graph_dependencies_have_correct_types():
    dependency_graph = DependencyGraph(MyComputeProcess)

    for name in EXPECTED_INPUTS:
        assert dependency_graph.inputs[name].value_type == "Number"
    for name in EXPECTED_INTERMEDIATES:
        assert dependency_graph.intermediates[name].value_type == "Number"
    assert dependency_graph.outputs[EXPECTED_OUTPUT].value_type == "Number"


def test_dependency_graph_serializes():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert dependency_graph.as_native() == EXPECTED_SERIALIZED_DEPENDENCY_GRAPH


def test_dependency_graph_serialization_matches_schema():
    import os
    import simplejson as json
    from jsonschema import RefResolver, Draft7Validator

    dependency_graph = DependencyGraph(MyComputeProcess)
    serialized = dependency_graph.as_native()

    with open(
        os.path.join(os.path.dirname(__file__), "generated", "schema.json"), "r"
    ) as f:
        schema = json.load(f)
    resolver = RefResolver.from_schema(schema)
    validator = Draft7Validator(
        {"$ref": "#/definitions/DependencyGraph"}, resolver=resolver
    )

    validator.validate(serialized)
