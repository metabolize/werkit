import inspect
import numbers
import typing as t
from typing_extensions import TypeGuard
from ._custom_value_type import CustomValueType


BuiltInValueType = t.Union[t.Type[bool], t.Type[int], t.Type[float], t.Type[str]]


def is_built_in_value_type(_type: t.Type) -> TypeGuard[BuiltInValueType]:
    return _type in (bool, int, float, numbers.Number, str)


def coerce_value_to_builtin_type(
    name: str, value_type: BuiltInValueType, value: t.Any
) -> t.Any:
    if not is_built_in_value_type(value_type):
        raise ValueError(
            "Expected built_in_value_type to be a valid built-in value type"
        )
    elif type(value) is value_type:
        return value
    else:
        raise ValueError(
            f"{name} should be type {value_type.__name__}, not {type(value).__name__}"
        )


AnyValueType = t.Union[BuiltInValueType, t.Type[CustomValueType]]


def assert_valid_value_type(value_type: AnyValueType) -> None:
    if is_built_in_value_type(value_type) or (
        inspect.isclass(value_type) and issubclass(value_type, CustomValueType)
    ):
        return
    raise ValueError(
        "Expected value type to be bool, int, float, str, or a subclass of CustomValueType"
    )
