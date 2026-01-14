import datetime
import typing as t
from ._types import (
    WerkitErrorOrigin,
    WerkitErrorOutputMessage,
    WerkitSuccessOutputMessage,
)


ResultType = t.TypeVar("ResultType")
MessageKeyType = t.TypeVar("MessageKeyType")


def serialize_result(
    message_key: t.Any,
    serializable_result: t.Any,
    start_time: datetime.datetime,
    duration_seconds: float,
    runtime_info: t.Any = None,
) -> WerkitSuccessOutputMessage[ResultType, MessageKeyType]:
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
    message_key: t.Any,
    exception: BaseException,
    error_origin: WerkitErrorOrigin,
    start_time: datetime.datetime,
    duration_seconds: float = -1,
    runtime_info: t.Any = None,
) -> WerkitErrorOutputMessage[MessageKeyType]:
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
    from ._synthetic_error import SyntheticError

    if isinstance(exception, SyntheticError):
        error = exception.error
        out_error_origin = exception.error_origin
    else:
        error = traceback.format_exception(None, exception, exception.__traceback__)
        out_error_origin = error_origin

    return {
        "message_key": message_key,
        "success": False,
        "result": None,
        "error": error,
        "error_origin": out_error_origin,
        "duration_seconds": duration_seconds,
        "start_time": start_time.astimezone().isoformat(),
        "runtime_info": runtime_info,
    }
