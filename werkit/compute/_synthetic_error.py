from ._types import WerkitErrorOrigin, WerkitErrorOutputMessage


class SyntheticError(Exception):
    """An exception that wraps a serialized error output message.

    This is useful for passing along an error output message that was
    generated elsewhere, such as in a subprocess.

    Only the message's `error` and `error_origin` keys are preserved.
    """

    error: list[str]
    error_origin: WerkitErrorOrigin

    def __init__(self, output_message: WerkitErrorOutputMessage):
        assert output_message["success"] is False
        self.error = output_message["error"]
        self.error_origin = output_message["error_origin"]
        super().__init__("".join(self.error))
