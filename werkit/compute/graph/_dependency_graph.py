from __future__ import annotations
import inspect
import numbers
import typing as t
from typing_extensions import Literal, TypedDict
from ._built_in_type import (
    BuiltInValueType,
    coerce_value_to_builtin_type,
    is_built_in_value_type,
)
from ._custom_type import CustomType, JSONType


AnyValueType = t.Union[BuiltInValueType, t.Type[CustomType]]


class BaseNode:
    def __init__(self, value_type: AnyValueType):
        if is_built_in_value_type(value_type) or (
            inspect.isclass(value_type) and issubclass(value_type, CustomType)
        ):
            self.value_type = value_type
        else:
            raise ValueError(
                "Expected value type to be bool, int, float, str, or a subclass of CustomType"
            )

    @property
    def value_type_is_built_in(self) -> bool:
        return is_built_in_value_type(self.value_type)

    @property
    def value_type_name(self) -> str:
        if self.value_type_is_built_in:
            if self.value_type is bool:
                return "boolean"
            elif self.value_type in (int, float, numbers.Number):
                return "number"
            elif self.value_type is str:
                return "string"
            else:
                raise ValueError("How did we get here?")
        else:
            return self.value_type.__name__

    def deserialize(self, value: JSONType) -> t.Any:
        if self.value_type_is_built_in:
            return value
        else:
            value_type = t.cast(t.Type[CustomType], self.value_type)
            value_type.validate(value)
            return value_type.deserialize(value)

    def coerce(self, name: str, value: t.Any) -> t.Any:
        if self.value_type_is_built_in:
            return coerce_value_to_builtin_type(
                name=name,
                value_type=t.cast(BuiltInValueType, self.value_type),
                value=value,
            )
        else:
            # TODO: Perhaps catch and re-throw to improve the error message.
            return t.cast(t.Type[CustomType], self.value_type).coerce(value)

    def serialize_value(self, value: t.Any) -> JSONType:
        if self.value_type_is_built_in:
            return value
        else:
            value_type = t.cast(t.Type[CustomType], self.value_type)
            serialized = value_type.serialize(value)
            value_type.validate(serialized)
            return serialized


InputJSONType = TypedDict("InputJSONType", {"valueType": str})


class Input(BaseNode):
    def serialize(self) -> InputJSONType:
        return {"valueType": self.value_type_name}


ComputeNodeJSONType = TypedDict(
    "ComputeNodeJSONType", {"valueType": str, "dependencies": t.List[str]}
)


class ComputeNode(BaseNode):
    # TODO: Use a narrower type for `method`.
    def __init__(self, method: t.Callable, value_type: AnyValueType):
        super().__init__(value_type=value_type)

        self.method = method
        self.dependencies = [x for x in inspect.signature(method).parameters.keys()][1:]

    def bind(self, instance: ComputeNode) -> t.Callable:
        import functools

        return functools.partial(self.method, instance)

    def serialize(self) -> ComputeNodeJSONType:
        return {
            "valueType": self.value_type_name,
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
    "DependencyGraphJSONType",
    {
        "schemaVersion": Literal[1],
        "inputs": t.Dict[str, InputJSONType],
        "intermediates": t.Dict[str, ComputeNodeJSONType],
        "outputs": t.Dict[str, ComputeNodeJSONType],
    },
)

AttrType = t.TypeVar("AttrType")


def _attrs_of_type(obj: t.Any, _type: t.Type[AttrType]) -> t.Dict[str, AttrType]:
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if not name.startswith("__") and isinstance(getattr(obj, name), _type)
    }


class DependencyGraph:
    def __init__(self, cls: t.Type):
        assert inspect.isclass(cls)

        self.inputs = _attrs_of_type(cls, Input)
        self.intermediates = _attrs_of_type(cls, Intermediate)
        self.outputs = _attrs_of_type(cls, Output)
        self.compute_nodes = dict(**self.intermediates, **self.outputs)
        self.all_nodes = dict(**self.inputs, **self.compute_nodes)

    def keys(self) -> t.List[str]:
        return list(self.inputs.keys()) + list(self.compute_nodes.keys())

    def serialize(self) -> DependencyGraphJSONType:
        return {
            "schemaVersion": 1,
            "inputs": {k: v.serialize() for k, v in self.inputs.items()},
            "intermediates": {k: v.serialize() for k, v in self.intermediates.items()},
            "outputs": {k: v.serialize() for k, v in self.outputs.items()},
        }
