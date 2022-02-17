SUPPORTED_TYPES = ["Number", "Point", "Measurement"]


def assert_valid_value_type(value_type: str) -> None:
    if value_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unknown value type: {value_type}")
