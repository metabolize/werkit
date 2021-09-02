def serialize_result(
    message_key, serializable_result, start_time, duration_seconds, runtime_info=None
):
    """
    Wrap the computation result in the `werkit.Manager` result schema.

    Args:
        serializable_result (object): Any serializable result.
        start_time (datetime.datetime): The start time of the computation.
        duration_seconds (int): The computation time.
        runtime_info (object): Serializable runtime metadata.
    """
    return {
        "message_key": message_key,
        "success": True,
        "result": serializable_result,
        "error": None,
        "error_origin": None,
        "start_time": start_time.astimezone().isoformat(),
        "duration_seconds": duration_seconds,
        "runtime_info": runtime_info,
    }


def serialize_exception(
    message_key,
    exception,
    error_origin,
    start_time,
    duration_seconds=-1,
    runtime_info=None,
):
    """
    Wrap an exception in the `werkit.Manager` result schema.

    Args:
        exception (Exception): The exception to wrap.
        error_origin (str): Either `"compute"`, `"system"` or
            `"orchestration"`. Refer to the `werkit.Manager` documentation for
            the definitions.
        start_time (datetime.datetime): The start time of the computation.
        duration_seconds (int): The time elapsed before the error occurred,
            if known.
        runtime_info (object): Serializable runtime metadata.
    """
    import traceback

    return {
        "message_key": message_key,
        "success": False,
        "result": None,
        "error": traceback.format_exception(None, exception, exception.__traceback__),
        "error_origin": error_origin,
        "duration_seconds": duration_seconds,
        "start_time": start_time.astimezone().isoformat(),
        "runtime_info": runtime_info,
    }
