from __future__ import annotations
import inspect
import numbers
import sys
import typing as t

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

from ._built_in_type import (
    BuiltInValueType,
    built_in_value_type_with_name,
    coerce_value_to_builtin_type,
    is_built_in_value_type,
)
from ._custom_type import CustomType, JSONType


def _attrs_of_type(obj: t.Any, _type: t.Type[AttrType]) -> dict[str, AttrType]:
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if not name.startswith("__") and isinstance(getattr(obj, name), _type)
    }


def _find_duplicates(items: list[str]) -> list[str]:
    from collections import Counter

    counter = Counter(items)
    return [item for item in counter if counter[item] > 1]


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
            return self.value_type.name

    def deserialize(self, value: JSONType) -> t.Any:
        if self.value_type_is_built_in:
            return value
        else:
            value_type = t.cast(t.Type[CustomType], self.value_type)
            value_type.validate(value)
            return value_type.deserialize(value)

    def normalize(self, name: str, value: t.Any) -> t.Any:
        if self.value_type_is_built_in:
            return coerce_value_to_builtin_type(
                name=name,
                value_type=t.cast(BuiltInValueType, self.value_type),
                value=value,
            )
        else:
            # TODO: Perhaps catch and re-throw to improve the error message.
            return t.cast(t.Type[CustomType], self.value_type).normalize(value)

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


def intermediate(value_type: AnyValueType) -> t.Callable[[t.Callable], Intermediate]:
    def decorator(method: t.Callable[..., t.Any]) -> Intermediate:
        return Intermediate(method, value_type)

    return decorator


def output(value_type: AnyValueType) -> t.Callable[[t.Callable], Output]:
    def decorator(method: t.Callable[..., t.Any]) -> Output:
        return Output(method, value_type)

    return decorator


AttrType = t.TypeVar("AttrType")


DependencyGraphJSONType = TypedDict(
    "DependencyGraphJSONType",
    {
        "schemaVersion": Literal[1],
        "inputs": t.Dict[str, InputJSONType],
        "intermediates": t.Dict[str, ComputeNodeJSONType],
        "outputs": t.Dict[str, ComputeNodeJSONType],
    },
)


def not_implemented() -> t.NoReturn:
    raise NotImplementedError("Deserialized compute nodes are not implemented")


def create_unimplemented_node(
    cls: t.Union[type[Input], type[Intermediate], type[Output]],
    value_type_name: str,
    custom_types: dict[str, type[CustomType]],
) -> AnyValueType:
    try:
        value_type = custom_types[value_type_name]
    except KeyError:
        value_type = built_in_value_type_with_name(value_type_name)

    if cls is Input:
        return cls(value_type=value_type)
    else:
        return cls(method=not_implemented, value_type=value_type)


class DependencyGraph:
    def __init__(
        self,
        inputs: dict[str, Input],
        intermediates: dict[str, Intermediate],
        outputs: dict[str, Output],
    ):
        self.inputs = inputs
        self.intermediates = intermediates
        self.outputs = outputs
        self.compute_nodes = dict(**self.intermediates, **self.outputs)
        self.all_nodes = dict(**self.inputs, **self.compute_nodes)

    @classmethod
    def from_class(cls: type[DependencyGraph], in_class: t.Type) -> "DependencyGraph":
        assert inspect.isclass(in_class)

        return cls(
            inputs=_attrs_of_type(in_class, Input),
            intermediates=_attrs_of_type(in_class, Intermediate),
            outputs=_attrs_of_type(in_class, Output),
        )

    @classmethod
    def deserialize(
        cls: type[DependencyGraph],
        data: DependencyGraphJSONType,
        custom_types: list[type[CustomType]] = [],
    ) -> "DependencyGraph":
        custom_type_names = [item.name for item in custom_types]
        duplicates = _find_duplicates(custom_type_names)
        if duplicates:
            raise ValueError(
                f"Duplicate custom type names found: {', '.join(duplicates)}"
            )
        keyed_custom_types = {[item.name]: item for item in custom_types}

        return cls(
            inputs={
                name: create_unimplemented_node(
                    cls=Input,
                    value_type_name=input_data["valueType"],
                    custom_types=keyed_custom_types,
                )
                for name, input_data in data["inputs"].items()
            },
            intermediates={
                name: create_unimplemented_node(
                    cls=Intermediate,
                    value_type_name=input_data["valueType"],
                    custom_types=keyed_custom_types,
                )
                for name, input_data in data["intermediates"].items()
            },
            outputs={
                name: create_unimplemented_node(
                    cls=Output,
                    value_type_name=input_data["valueType"],
                    custom_types=keyed_custom_types,
                )
                for name, input_data in data["outputs"].items()
            },
        )

    def keys(self) -> t.List[str]:
        return list(self.inputs.keys()) + list(self.compute_nodes.keys())

    def serialize(self) -> DependencyGraphJSONType:
        return {
            "schemaVersion": 1,
            "inputs": {k: v.serialize() for k, v in self.inputs.items()},
            "intermediates": {k: v.serialize() for k, v in self.intermediates.items()},
            "outputs": {k: v.serialize() for k, v in self.outputs.items()},
        }
