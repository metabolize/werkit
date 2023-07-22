import datetime
import os
import time
import typing as t


def env_flag(env_var: str, default: bool) -> bool:
    environ_string = os.environ.get(env_var, "").strip().lower()
    if not environ_string:
        return default
    return environ_string in ["1", "true", "yes", "on"]


DELAY_SECONDS = int(os.environ.get("DELAY_SECONDS", "0"))
SHOULD_THROW = env_flag("SHOULD_THROW", False)


def serialize_result(message_key: t.Any, result: t.Any) -> dict[str, t.Any]:
    """
    Simulate the effect of `werkit.Manager()`, which is not used here so this
    test service can be kept to one file.

    TODO: Improve this example by consuming a real schema.
    """
    return {
        "message_key": message_key,
        "success": True,
        "result": result,
        "error": None,
        "error_origin": None,
        "start_time": datetime.datetime(2019, 12, 31).astimezone().isoformat(),
        "duration_seconds": 1.0,
        "runtime_info": None,
    }


def handler(event: dict[str, t.Any], context: dict[str, t.Any]) -> dict[str, t.Any]:
    print("event", event)

    time.sleep(DELAY_SECONDS)
    if SHOULD_THROW:
        raise Exception("Whoops!")

    result = event["base"] ** event["exponent"]

    serialized = serialize_result(message_key=event["message_key"], result=result)
    print("serialized", serialized)
    return serialized
