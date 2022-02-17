import inspect
from ._types import Input
from ._decorators import Intermediate, Output


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
