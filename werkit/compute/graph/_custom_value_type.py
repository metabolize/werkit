from __future__ import annotations
import typing as t
from abc import ABC, abstractmethod

JSONType = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]


class CustomValueType(ABC):
    @abstractmethod
    def to_json(self) -> JSONType:
        pass

    @classmethod
    @abstractmethod
    def validate_json(cls, json_value: JSONType) -> None:
        pass

    @classmethod
    @abstractmethod
    def from_valid_json(cls, json_value: JSONType) -> CustomValueType:
        pass

    @classmethod
    def from_json(cls, json_value: JSONType) -> CustomValueType:
        cls.validate_json(json_value=json_value)
        return cls.from_valid_json(json_value)

    @classmethod
    def coerce(cls, name: str, value: t.Any) -> CustomValueType:
        raise ValueError(
            f"{name} should be coercible to type {cls.__name__}, got {type(value).__name__}"
        )
