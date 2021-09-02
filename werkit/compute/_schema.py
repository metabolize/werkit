class Schema:
    """
    Helper for validating request, result, and serialized result schemas
    """

    def __init__(
        self, schema, request_ref=None, result_ref=None, serialized_result_ref=None
    ):
        from jsonschema import RefResolver

        self.resolver = RefResolver.from_schema(schema)
        self.request = None if request_ref is None else self.validator_for(request_ref)
        self.result = None if result_ref is None else self.validator_for(result_ref)
        self.serialized_result = (
            None
            if serialized_result_ref is None
            else self.validator_for(serialized_result_ref)
        )

    @classmethod
    def load_from_path(cls, schema_filename, **kwargs):
        import simplejson as json

        with open(schema_filename, "r") as f:
            return cls(schema=json.load(f), **kwargs)

    @classmethod
    def load_relative_to_file(cls, file_obj, path_components, **kwargs):
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
            **kwargs
        )

    def validator_for(self, ref):
        from jsonschema import Draft7Validator

        return Draft7Validator({"$ref": ref}, resolver=self.resolver)
