import numbers
import typing as t

BuiltInValueType = t.Union[t.Type[bool], t.Type[int], t.Type[float], t.Type[str]]

BuiltInValueTypeName = t.Literal["bool", "number", "string"]


def is_built_in_value_type(_type: t.Type) -> t.TypeGuard[BuiltInValueType]:
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


def built_in_value_type_with_name(name: BuiltInValueTypeName) -> BuiltInValueType:
    try:
        return {
            "boolean": bool,
            "number": numbers.Number,
            "string": str,
        }[name]
    except KeyError:
        raise KeyError(f"Unknown value type: {name}")
