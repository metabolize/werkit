from __future__ import annotations
import inspect
import numbers
import typing as t
from typing_extensions import TypeGuard
from abc import ABC, abstractmethod

JSONType = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]


class BaseValue(ABC):
    @abstractmethod
    def to_json(self) -> JSONType:
        pass

    @classmethod
    @abstractmethod
    def validate_json(cls, json_value: JSONType) -> None:
        pass

    @classmethod
    @abstractmethod
    def from_valid_json(cls, json_value: JSONType) -> BaseValue:
        pass

    @classmethod
    def from_json(cls, json_value: JSONType) -> BaseValue:
        cls.validate_json(json_value=json_value)
        return cls.from_valid_json(json_value)

    @classmethod
    def coerce(cls, name: str, value: t.Any) -> BaseValue:
        raise ValueError(
            f"{name} should be coercible to type {cls.__name__}, got {type(value).__name__}"
        )


BuiltInValueType = t.Union[t.Type[bool], t.Type[int], t.Type[float], t.Type[str]]


def is_built_in_value_type(_type: t.Type) -> TypeGuard[BuiltInValueType]:
    return _type in (bool, int, float, numbers.Number, str)


def coerce_value(
    name: str, built_in_value_type: BuiltInValueType, value: t.Any
) -> t.Any:
    if not is_built_in_value_type(built_in_value_type):
        raise ValueError(
            "Expected built_in_value_type to be a valid built-in value type"
        )
    elif type(value) is built_in_value_type:
        return value
    else:
        raise ValueError(
            f"{name} should be type {built_in_value_type.__name__}, not {type(value).__name__}"
        )


AnyValueType = t.Union[BuiltInValueType, t.Type[BaseValue]]


def assert_valid_value_type(value_type: AnyValueType) -> None:
    if is_built_in_value_type(value_type) or (
        inspect.isclass(value_type) and issubclass(value_type, BaseValue)
    ):
        return
    raise ValueError(
        "Expected value type to be bool, int, float, str, or a subclass of BaseValue"
    )


def value_type_to_str(value_type: AnyValueType) -> str:
    assert_valid_value_type(value_type)

    if issubclass(value_type, BaseValue):
        return value_type.__name__
    elif value_type is bool:
        return "Boolean"
    elif value_type in (int, float, numbers.Number):
        return "Number"
    elif value_type is str:
        return "String"
    else:
        raise ValueError("How did we get here?")
