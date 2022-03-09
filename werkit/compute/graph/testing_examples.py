from . import Input, bind_state_manager, intermediate, output


@bind_state_manager()
class MyComputeProcess:
    a = Input(value_type=int)
    b = Input(value_type=int)

    @intermediate(value_type=int)
    def i(self, a):
        return a

    @intermediate(value_type=int)
    def j(self, b):
        return b

    @output(value_type=int)
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


class MyRaisingComputeProcess(MyComputeProcess):
    @output(value_type=int)
    def s(self):
        raise ValueError("Whoops")

    @output(value_type=int)
    def t(self):
        raise ValueError("Whoops")


class MyWronglyTypedComputeProcess(MyComputeProcess):
    @output(value_type=int)
    def s(self):
        return False
