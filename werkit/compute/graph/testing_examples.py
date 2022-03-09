from . import Input, bind_state_manager, intermediate, output


@bind_state_manager()
class MyComputeProcess:
    a = Input(value_type=float)
    b = Input(value_type=float)

    @intermediate(value_type=float)
    def i(self, a):
        return a

    @intermediate(value_type=float)
    def j(self, b):
        return b

    @output(value_type=float)
    def r(self, i, j):
        return i + j


EXPECTED_INPUTS = ["a", "b"]
EXPECTED_INTERMEDIATES = ["i", "j"]
EXPECTED_OUTPUT = "r"

EXPECTED_SERIALIZED_DEPENDENCY_GRAPH = {
    "schemaVersion": 1,
    "inputs": {"a": {"valueType": "Number"}, "b": {"valueType": "Number"}},
    "intermediates": {
        "i": {"valueType": "Number", "dependencies": ["a"]},
        "j": {"valueType": "Number", "dependencies": ["b"]},
    },
    "outputs": {"r": {"valueType": "Number", "dependencies": ["i", "j"]}},
}


class MyComputeProcessSubclass(MyComputeProcess):
    pass


class MyErroringComputeProcess(MyComputeProcess):
    @output(value_type=float)
    def s(self):
        raise ValueError("Whoops")

    @output(value_type=float)
    def t(self):
        raise ValueError("Whoops")
