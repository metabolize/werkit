import time
import os


def env_flag(env_var, default):
    import os

    environ_string = os.environ.get(env_var, "").strip().lower()
    if not environ_string:
        return default
    return environ_string in ["1", "true", "yes", "on"]


DELAY_SECONDS = int(os.environ.get("DELAY_SECONDS", "0"))
SHOULD_THROW = env_flag("SHOULD_THROW", False)


def wrap_result(serializable_result):
    """
    Simulate the effect of `werkit.Manager()`, which is not used here so this
    test service can be kept to one file.
    """
    return {
        "success": True,
        "result": serializable_result,
        "error": None,
        "error_origin": None,
        "duration_seconds": 1.0,
        "runtime_info": None,
    }


def handler(event, context):
    time.sleep(DELAY_SECONDS)
    if SHOULD_THROW:
        raise Exception("Whoops!")

    return wrap_result(event["input"] + sum(event["extra_args"]))
