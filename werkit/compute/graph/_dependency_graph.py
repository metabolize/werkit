import inspect
from ._types import assert_valid_type


class Input:
    def __init__(self, _type):
        assert_valid_type(_type)
        self._type = _type

    def as_native(self):
        return {"type": self._type}


class InnerNode:
    def __init__(self, method, _type):
        self.method = method

        assert_valid_type(_type)
        self._type = _type

        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def bind(self, instance):
        import functools

        return functools.partial(self.method, instance)

    def as_native(self):
        return {"type": self._type, "dependencies": self.dependencies}


class Intermediate(InnerNode):
    pass


class Output(InnerNode):
    pass


def intermediate(_type: str):
    def decorator(method):
        return Intermediate(method, _type)

    return decorator


def output(_type: str):
    def decorator(method):
        return Output(method, _type)

    return decorator


def attrs_of_type(obj, _type):
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if not name.startswith("__") and isinstance(getattr(obj, name), _type)
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
