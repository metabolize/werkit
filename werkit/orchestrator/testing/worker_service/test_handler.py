from werkit.compute import Schema
from .handler import handler

EXAMPLE_EVENT = {"message_key": None, "base": 2, "exponent": 10}
EXAMPLE_RESULT = 2 ** 10

schema = Schema.load_relative_to_file(__file__, ["generated", "schema.json"])


def test_worker_service_success() -> None:
    # Confidence check.
    schema.input_message.validate(EXAMPLE_EVENT)

    result = handler(event=EXAMPLE_EVENT, context={})
    schema.output_message.validate(result)

    assert result["result"] == EXAMPLE_RESULT
