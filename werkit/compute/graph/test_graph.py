from . import Input, intermediate, output, StateManager, DependencyGraph


class MyComputeProcess:
    a = Input(_type="Number")
    b = Input(_type="Number")

    def __init__(self):
        self.state_manager = StateManager(self)

    @intermediate(_type="Number")
    def i(self, a):
        return a

    @intermediate(_type="Number")
    def j(self, b):
        return b

    @output(_type="Number")
    def r(self, i, j):
        return i + j


expected_inputs = ["a", "b"]
expected_intermediates = ["i", "j"]
expected_output = "r"


def test_dependency_graph_collects_dependencies():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert set(dependency_graph.inputs.keys()) == set(expected_inputs)
    assert set(dependency_graph.intermediates.keys()) == set(expected_intermediates)
    assert set(dependency_graph.outputs.keys()) == set([expected_output])


def test_dependency_graph_dependencies_have_correct_types():
    dependency_graph = DependencyGraph(MyComputeProcess)

    for name in expected_inputs:
        assert dependency_graph.inputs[name]._type == "Number"
    for name in expected_intermediates:
        assert dependency_graph.intermediates[name]._type == "Number"
    assert dependency_graph.outputs["r"]._type == "Number"


def test_dependency_graph_serializes():
    dependency_graph = DependencyGraph(MyComputeProcess)

    assert dependency_graph.as_native() == {
        "schemaVersion": 1,
        "inputs": {"a": {"type": "Number"}, "b": {"type": "Number"}},
        "intermediates": {
            "i": {"type": "Number", "dependencies": ["a"]},
            "j": {"type": "Number", "dependencies": ["b"]},
        },
        "outputs": {"r": {"type": "Number", "dependencies": ["i", "j"]}},
    }


def test_graph_has_state_manager():
    assert isinstance(MyComputeProcess().state_manager, StateManager)
