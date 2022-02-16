SUPPORTED_TYPES = ["Number", "Point", "Measurement"]


def assert_valid_type(_type: str) -> None:
    if _type not in SUPPORTED_TYPES:
        raise ValueError(f"Unknown type: {_type}")


class Input:
    def __init__(self, _type):
        assert_valid_type(_type)
        self._type = _type

    def as_native(self):
        return {"type": self._type}
