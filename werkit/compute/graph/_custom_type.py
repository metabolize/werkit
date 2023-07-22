import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from jsonschema import Draft7Validator

CanonicalType = t.TypeVar("CanonicalType")


class CustomType(ABC, t.Generic[CanonicalType]):
    """
    While the canonical type could be the type class itself, this isn't required
    or even encouraged. Any existing type can be used as the canonical type,
    whereas the CustomType is responsible for canonicalization and
    serialization.
    """

    _validator: t.Optional["Draft7Validator"]

    @classmethod
    def name(cls) -> str:
        """
        The name of the custom type, used in the serialized dependency graph.
        The default is `cls.__name__`.
        """
        return cls.__name__

    @classmethod
    def schema_path(cls) -> str:
        """
        The path to the JSON schema. The default is 'generated/schema.json',
        relative to the file where the class is defined.
        """
        import inspect
        import os

        return os.path.join(
            os.path.dirname(inspect.getfile(cls)), "generated", "schema.json"
        )

    @classmethod
    def ref(cls) -> str:
        """
        The ref to look up in the JSON schema. The default is
        '#/definitions/{cls.name()}'.
        """
        return f"#/definitions/{cls.name()}"

    @classmethod
    def validate(cls, json_data: t.Any) -> None:
        """
        Validate the JSON representation.
        """
        from missouri import json
        from jsonschema import Draft7Validator, RefResolver

        try:
            validator = t.cast(Draft7Validator, cls._validator)
        except AttributeError:
            schema = json.load(cls.schema_path())
            resolver = RefResolver.from_schema(schema)
            validator = cls._validator = Draft7Validator(
                {"$ref": cls.ref()}, resolver=resolver
            )

        validator.validate(json_data)

    @classmethod
    @abstractmethod
    def deserialize(cls, json_data: t.Any) -> CanonicalType:
        """
        Convert the JSON representation to the canonical native type.
        """

    @classmethod
    @abstractmethod
    def normalize(cls, value: t.Any) -> CanonicalType:
        """
        Coerce the given value to the canonical native type. Raise an exception
        if it can't be normalized.
        """

    @classmethod
    @abstractmethod
    def serialize(self, value: CanonicalType) -> t.Any:
        """
        Convert the canonical native type to a JSON representation.
        """
