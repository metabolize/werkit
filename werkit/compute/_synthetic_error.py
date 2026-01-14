from ._types import WerkitErrorOrigin, WerkitErrorOutputMessage


class SyntheticError(Exception):
    """An exception that wraps a serialized error output message.

    This is useful for passing along an error output message that was
    generated elsewhere, such as in a subprocess.

    Only the message's `error` key is preserved.
    """

    error_origin: WerkitErrorOrigin
    error: list[str]

    def __init__(self, output_message: WerkitErrorOutputMessage):
        assert output_message["success"] is False
        self.error = output_message["error"]
        super().__init__("".join(self.error))
