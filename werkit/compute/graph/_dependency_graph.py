import inspect
from ._value_types import assert_valid_value_type


class Input:
    def __init__(self, value_type):
        assert_valid_value_type(value_type)
        self.value_type = value_type

    def as_native(self):
        return {"valueType": self.value_type}


class InnerNode:
    def __init__(self, method, value_type):
        self.method = method

        assert_valid_value_type(value_type)
        self.value_type = value_type

        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def bind(self, instance):
        import functools

        return functools.partial(self.method, instance)

    def as_native(self):
        return {"valueType": self.value_type, "dependencies": self.dependencies}


class Intermediate(InnerNode):
    pass


class Output(InnerNode):
    pass


def intermediate(value_type: str):
    def decorator(method):
        return Intermediate(method, value_type)

    return decorator


def output(value_type: str):
    def decorator(method):
        return Output(method, value_type)

    return decorator


def attrs_of_type(obj, value_type):
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if not name.startswith("__") and isinstance(getattr(obj, name), value_type)
    }


class DependencyGraph:
    def __init__(self, cls):
        assert inspect.isclass(cls)

        self.inputs = attrs_of_type(cls, Input)
        self.intermediates = attrs_of_type(cls, Intermediate)
        self.outputs = attrs_of_type(cls, Output)
        self.compute_nodes = dict(**self.intermediates, **self.outputs)

    def keys(self):
        return list(self.inputs.keys()) + list(self.compute_nodes.keys())

    def as_native(self):
        return {
            "schemaVersion": 1,
            "inputs": {k: v.as_native() for k, v in self.inputs.items()},
            "intermediates": {k: v.as_native() for k, v in self.intermediates.items()},
            "outputs": {k: v.as_native() for k, v in self.outputs.items()},
        }
