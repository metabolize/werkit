from __future__ import annotations
import inspect
import typing as t
from typing_extensions import TypedDict
from ._value_types import (
    AnyValueType,
    BUILT_IN_VALUE_TYPES,
    coerce_value,
    assert_valid_value_type,
    value_type_to_str,
)


class BaseNode:
    def __init__(self, value_type: AnyValueType):
        assert_valid_value_type(value_type)
        self.value_type = value_type

    def coerce(self, name: str, value: any) -> t.Any:
        if self.value_type in BUILT_IN_VALUE_TYPES:
            return coerce_value(
                name=name, built_in_value_type=self.value_type, value=value
            )
        else:
            return self.value_type.coerce(name=name, value=value)


InputJSONType = TypedDict("Input", {"valueType": str})


class Input(BaseNode):
    def as_native(self) -> InputJSONType:
        return {"valueType": value_type_to_str(self.value_type)}


ComputeNodeJSONType = TypedDict(
    "ComputeNode", {"valueType": str, "dependencies": t.List[str]}
)


class ComputeNode(BaseNode):
    def __init__(self, method, value_type: AnyValueType):
        super().__init__(value_type=value_type)

        self.method = method
        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def bind(self, instance: ComputeNode):
        import functools

        return functools.partial(self.method, instance)

    def as_native(self) -> ComputeNodeJSONType:
        return {
            "valueType": value_type_to_str(self.value_type),
            "dependencies": self.dependencies,
        }


class Intermediate(ComputeNode):
    pass


class Output(ComputeNode):
    pass


def intermediate(value_type: AnyValueType):
    def decorator(method):
        return Intermediate(method, value_type)

    return decorator


def output(value_type: AnyValueType):
    def decorator(method):
        return Output(method, value_type)

    return decorator


DependencyGraphJSONType = TypedDict(
    "DependencyGraph",
    {
        "schemaVersion": t.Literal[1],
        "inputs": t.Dict[str, InputJSONType],
        "intermediates": t.Dict[str, ComputeNodeJSONType],
        "outputs": t.Dict[str, ComputeNodeJSONType],
    },
)


def _attrs_of_type(obj, _type: t.Type):
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if not name.startswith("__") and isinstance(getattr(obj, name), _type)
    }


class DependencyGraph:
    def __init__(self, cls):
        assert inspect.isclass(cls)

        self.inputs = _attrs_of_type(cls, Input)
        self.intermediates = _attrs_of_type(cls, Intermediate)
        self.outputs = _attrs_of_type(cls, Output)
        self.compute_nodes = dict(**self.intermediates, **self.outputs)
        self.all_nodes = dict(**self.inputs, **self.compute_nodes)

    def keys(self) -> t.List[str]:
        return list(self.inputs.keys()) + list(self.compute_nodes.keys())

    def as_native(self) -> DependencyGraphJSONType:
        return {
            "schemaVersion": 1,
            "inputs": {k: v.as_native() for k, v in self.inputs.items()},
            "intermediates": {k: v.as_native() for k, v in self.intermediates.items()},
            "outputs": {k: v.as_native() for k, v in self.outputs.items()},
        }
