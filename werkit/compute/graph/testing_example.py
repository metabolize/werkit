from . import Input, intermediate, output, StateManager, Bound


class MyComputeProcess(Bound):
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


EXPECTED_INPUTS = ["a", "b"]
EXPECTED_INTERMEDIATES = ["i", "j"]
EXPECTED_OUTPUT = "r"

EXPECTED_SERIALIZED_TREE = {
    "schemaVersion": 1,
    "inputs": {"a": {"type": "Number"}, "b": {"type": "Number"}},
    "intermediates": {
        "i": {"type": "Number", "dependencies": ["a"]},
        "j": {"type": "Number", "dependencies": ["b"]},
    },
    "outputs": {"r": {"type": "Number", "dependencies": ["i", "j"]}},
}
