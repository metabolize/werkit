from . import DependencyGraph
from .testing_examples import (
    EXPECTED_INPUTS,
    EXPECTED_INTERMEDIATES,
    EXPECTED_OUTPUT,
    EXPECTED_SERIALIZED_DEPENDENCY_GRAPH,
    MyComputeProcess,
)


def test_dependency_graph_collects_dependencies() -> None:
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert set(dependency_graph.inputs.keys()) == set(EXPECTED_INPUTS)
    assert set(dependency_graph.intermediates.keys()) == set(EXPECTED_INTERMEDIATES)
    assert set(dependency_graph.outputs.keys()) == set([EXPECTED_OUTPUT])


def test_dependency_graph_dependencies_have_correct_types() -> None:
    dependency_graph = DependencyGraph(MyComputeProcess)

    for name in EXPECTED_INPUTS:
        assert dependency_graph.inputs[name].value_type is int
    for name in EXPECTED_INTERMEDIATES:
        assert dependency_graph.intermediates[name].value_type is int
    assert dependency_graph.outputs[EXPECTED_OUTPUT].value_type is int


def test_dependency_graph_serializes() -> None:
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert dependency_graph.as_native() == EXPECTED_SERIALIZED_DEPENDENCY_GRAPH


def test_dependency_graph_serialization_matches_schema() -> None:
    import os
    import simplejson as json
    from jsonschema import RefResolver, Draft7Validator

    dependency_graph = DependencyGraph(MyComputeProcess)
    serialized = dependency_graph.as_native()

    with open(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "types",
            "src",
            "generated",
            "dependency-graph.schema.json",
        ),
        "r",
    ) as f:
        schema = json.load(f)
    resolver = RefResolver.from_schema(schema)
    validator = Draft7Validator(
        {"$ref": "#/definitions/DependencyGraphWithBuiltinTypes"}, resolver=resolver
    )

    validator.validate(serialized)
