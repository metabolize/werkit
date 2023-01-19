# from werkit.compute import Schema
from werkit.compute._schema import Schema

SCHEMA = Schema.load_relative_to_file(
    __file__,
    ["generated", "schema.json"],
    output_ref="#/definitions/AnyOutput",
)
