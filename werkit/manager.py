import datetime
import sys
from .formatting import format_time
from .schema import wrap_exception, wrap_result


class Manager:
    """
    Wrap a bit of cloud or batch computation, automatically handling and
    serializing errors and timing the computation.

    Always returns a dictionary with the following keys:

    - `success` (`bool`): `True` so long as no exception was raised.
    - `result` (`object`): In case of succes, the deserialized result.
    - `error` (`None` or `list`): In case of an error, the formatted exception
        traceback.
    - `error_origin` (`None` or `str`): In case of an error, the source of the
        error, which is `'compute'` for errors which originate inside the
        context handler. Other values are reserved (but unsued by this
        function): `'system'` for errors on the compute system which are
        external to the compute code, and `'orchestration'` for other errors
        which occur while attempting to reach the remote system, including
        timeouts.
    - `start_time` (`str`): The local start time of the computation, in ISO
        8601 with the time zone.
    - `duration_seconds` (`float`): The time spent in computation.
    - `runtime_info` (`object`): User-provided runtime metadata.

    Args:
        handle_exceptions (bool): When `True`, exceptions thrown within the
            block are caught and serialized, as is useful for wrapping cloud
            processes or batch jobs, where you don't want to crash. When
            `False` these exceptions propagate, as is useful for development.
            `KeyboardInterrupt` and `SystemExit` exceptions always propagate.
        vebose (bool): When `True`, print out timing information when
            computation finishes.
        time_precision (int): The number of decimal places (of seconds) to
            include in the timing result. The default is 2, which rounds to
            the nearest hundredth of a second.

    Example:

        with Manager(handle_exceptions=handle_exceptions) as manager:
            result = perform_computation()
            # If needed, convert result to JSON-serializable objects.
            as_native = transform(result)
            manager.result = as_native
        return manager.serialized_result
    """

    def __init__(
        self, runtime_info=None, handle_exceptions=True, verbose=False, time_precision=2
    ):
        self.runtime_info = runtime_info
        self.handle_exceptions = handle_exceptions
        self.verbose = verbose
        self.time_precision = time_precision
        self.result = None

    def __enter__(self):
        self.start_time = datetime.datetime.now()
        return self

    def __exit__(self, type, value, traceback):
        duration_seconds = round(
            (datetime.datetime.now() - self.start_time).total_seconds(),
            self.time_precision,
        )

        if type in [KeyboardInterrupt, SystemExit]:
            raise value

        if value:
            self.serialized_result = wrap_exception(
                exception=value,
                error_origin="compute",
                start_time=self.start_time,
                duration_seconds=duration_seconds,
                runtime_info=self.runtime_info,
            )
            if self.handle_exceptions:
                print(
                    "Error handled by werkit. (To disable, invoke `Manager()` with `handle_exceptions=False`.)"
                )
                print("".join(self.serialized_result["error"]))
                return True
            else:
                return False
        else:
            self.serialized_result = wrap_result(
                serializable_result=self.result,
                start_time=self.start_time,
                duration_seconds=duration_seconds,
                runtime_info=self.runtime_info,
            )

        if self.verbose:
            print(
                "Completed in {}".format(format_time(duration_seconds)), file=sys.stderr
            )
