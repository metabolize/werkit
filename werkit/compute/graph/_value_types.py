from __future__ import annotations
import inspect
import typing as t
from abc import ABC, abstractclassmethod, abstractmethod

JSONType = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]


class BaseValue(ABC):
    @abstractmethod
    def to_json(self) -> JSONType:
        pass

    @abstractclassmethod
    def validate(cls, json_value: JSONType) -> None:
        pass

    @abstractclassmethod
    def from_json(cls, json_value: JSONType) -> BaseValue:
        pass


BuiltInValueType = t.Union[t.Type[bool], t.Type[int], t.Type[float], t.Type[str]]
AnyValueType = t.Union[BuiltInValueType, t.Type[BaseValue]]


def assert_valid_value_type(value_type: AnyValueType) -> None:
    if value_type in (bool, int, float, str):
        return
    if inspect.isclass(value_type) and issubclass(value_type, BaseValue):
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
    elif value_type in (int, float):
        return "Number"
    elif value_type is str:
        return "String"
    else:
        raise ValueError("How did we get here?")
