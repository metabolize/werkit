import typing as t
from typing_extensions import Unpack

if t.TYPE_CHECKING:  # pragma: no cover
    from jsonschema import Draft7Validator


class RefKwargs(t.TypedDict, total=False):
    input_message_ref: str
    output_ref: str
    output_message_ref: str


class Schema:
    """
    Helper for validating request, result, and serialized result schemas
    """

    def __init__(
        self,
        schema: t.Any,
        input_message_ref: str = "#/definitions/AnyInputMessage",
        output_ref: str = "#/definitions/Output",
        output_message_ref: str = "#/definitions/AnyOutputMessage",
    ):
        from jsonschema import RefResolver

        self.resolver = RefResolver.from_schema(schema)
        self.input_message = (
            None if input_message_ref is None else self.validator_for(input_message_ref)
        )
        self.output = None if output_ref is None else self.validator_for(output_ref)
        self.output_message = (
            None
            if output_message_ref is None
            else self.validator_for(output_message_ref)
        )

    @classmethod
    def load_from_path(
        cls, schema_filename: str, **kwargs: Unpack[RefKwargs]
    ) -> "Schema":
        from missouri import json

        return cls(schema=json.load(schema_filename), **kwargs)

    @classmethod
    def load_relative_to_file(
        cls, filename: str, path_components: list[str], **kwargs: Unpack[RefKwargs]
    ) -> "Schema":
        """
        By convention, the schema is placed in
        `types/src/generated/schema.json` relative to the handler.
        """
        import os

        return cls.load_from_path(
            schema_filename=os.path.join(
                os.path.dirname(filename),
                *path_components,
            ),
            **kwargs,
        )

    def validator_for(self, ref: str) -> "Draft7Validator":
        from jsonschema import Draft7Validator

        return Draft7Validator({"$ref": ref}, resolver=self.resolver)
