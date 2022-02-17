SUPPORTED_TYPES = ["Number", "Point", "Measurement"]


def assert_valid_type(_type: str) -> None:
    if _type not in SUPPORTED_TYPES:
        raise ValueError(f"Unknown type: {_type}")
