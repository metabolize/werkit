import typing as t

if t.TYPE_CHECKING:
    from jsonschema import Draft7Validator


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
    def load_from_path(cls, schema_filename: str, **kwargs) -> "Schema":
        import simplejson as json

        with open(schema_filename, "r") as f:
            return cls(schema=json.load(f), **kwargs)

    @classmethod
    def load_relative_to_file(cls, file_obj, path_components, **kwargs) -> "Schema":
        """
        By convention, the schema is placed in
        `types/src/generated/schema.json` relative to the handler.
        """
        import os

        return cls.load_from_path(
            schema_filename=os.path.join(
                os.path.dirname(file_obj),
                *path_components,
            ),
            **kwargs,
        )

    def validator_for(self, ref) -> "Draft7Validator":
        from jsonschema import Draft7Validator

        return Draft7Validator({"$ref": ref}, resolver=self.resolver)
