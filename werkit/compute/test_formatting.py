from ._formatting import format_time


def test_format_time() -> None:
    format_time(5.125) == "5.125 sec"
    format_time(125.125) == "2 min, 5.125 sec"
