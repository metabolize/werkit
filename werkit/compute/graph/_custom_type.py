import typing as t
from abc import ABC, abstractmethod

JSONType = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]

CanonicalNativeType = t.TypeVar("CanonicalNativeType")


class CustomType(ABC, t.Generic[CanonicalNativeType]):
    @classmethod
    def schema_path(cls):
        """
        The path to the JSON schema. The default is 'generated/schema.json',
        relative to the file where the class is defined.
        """
        import inspect
        import os

        return os.path.join(inspect.getfile(cls), "generated", "schema.json")

    @classmethod
    def ref(cls):
        """
        The ref to look up in the JSON schema. The default is
        '#/definitions/{cls.__name__}'.
        """
        return f"#/definitions/{cls.__name__}"

    @classmethod
    @abstractmethod
    def deserialize(cls, json_data: JSONType) -> CanonicalNativeType:
        """
        Convert the JSON representation to the canonical native type.
        """

    @classmethod
    @abstractmethod
    def coerce(cls, value: t.Any) -> CanonicalNativeType:
        """
        Coerce the given value to the canonical native type. Raise an exception
        if it can't be coerced.
        """

    @classmethod
    @abstractmethod
    def serialize(self, value: CanonicalNativeType) -> JSONType:
        """
        Convert the canonical native type to a JSON representation.
        """
