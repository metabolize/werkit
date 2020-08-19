def validate_result(result):
    """
    Validate that the result matches the schema for `werkit.Manager`.
    """
    expected_keys = [
        "success",
        "result",
        "error",
        "error_origin",
        "duration_seconds",
        "runtime_info",
    ]
    if not isinstance(result, dict):
        raise ValueError(
            f"Expected Lambda result to be a dict with {','.join(expected_keys)}; got {result}"
        )
    result_keys = result.keys()
    missing_keys = [k for k in expected_keys if k not in result_keys]
    if len(missing_keys) > 0:
        raise ValueError(
            f"Lambda result contained keys {', '.join(result_keys)}; missing {','.join(missing_keys)}"
        )
    if not isinstance(result["success"], bool):
        raise ValueError(
            f"Expected result[\"success\"] to be a bool, got {result['success']}"
        )
    allowed_error_origins = ["compute", "system", "orchestration"]
    if result["error_origin"] not in [None] + allowed_error_origins:
        raise ValueError(
            f"Expected result[\"error_origin\"] to be {','.join(allowed_error_origins)}, or `None`"
        )


def wrap_result(serializable_result, start_time, duration_seconds, runtime_info=None):
    """
    Wrap the computation result in the `werkit.Manager` result schema.

    Args:
        serializable_result (object): Any serializable result.
        start_time (datetime.datetime): The start time of the computation.
        duration_seconds (int): The computation time.
        runtime_info (object): Serializable runtime metadata.
    """
    return {
        "success": True,
        "result": serializable_result,
        "error": None,
        "error_origin": None,
        "start_time": start_time.astimezone().isoformat(),
        "duration_seconds": duration_seconds,
        "runtime_info": runtime_info,
    }


def wrap_exception(
    exception, error_origin, start_time, duration_seconds=-1, runtime_info=None
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
        "success": False,
        "result": None,
        "error": traceback.format_exception(None, exception, exception.__traceback__),
        "error_origin": error_origin,
        "duration_seconds": duration_seconds,
        "start_time": start_time.astimezone().isoformat(),
        "runtime_info": runtime_info,
    }
