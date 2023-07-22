import datetime
import sys
import typing as t
from types import TracebackType
from ._destination import Destination
from ._formatting import format_time
from ._schema import Schema
from ._serialization import serialize_exception, serialize_result

if t.TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Self


class Manager:
    """
    Wrap a bit of cloud or batch computation, automatically handling and
    serializing errors and timing the computation.

    Either set `manager.result` with the result of the computation or raise an
    exception. When the handler closes, `manager.output_message` will be a
    dictionary with the following keys:

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
        schema (werkit.compute.Schema): A helper object containing the
            request, result, and serialized result schemas.
        destination (werkit.compute.Destination): An optional destination
            to which the serialized result is dispatched.
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

        with Manager(
            input_message=params,
            schema=schema,
            handle_exceptions=handle_exceptions,
            verbose=verbose,
        ) as manager:
            result = perform_computation()
            # If needed, convert result to JSON-serializable objects.
            serialized = transform(result)
            manager.result = serialized
        return manager.output_message
    """

    def __init__(
        self,
        input_message: dict[str, t.Any],
        schema: Schema,
        destination: t.Optional[Destination] = None,
        runtime_info: t.Any = None,
        handle_exceptions: bool = True,
        verbose: bool = False,
        time_precision: int = 2,
    ):
        # Import late to avoid circular import.
        from werkit.compute import Destination, Schema

        if not isinstance(schema, Schema):
            raise ValueError(
                "Expected schema to be an instance of werkit.compute.Schema"
            )
        self.schema = schema

        if destination is not None and not isinstance(destination, Destination):
            raise ValueError(
                "Expected destination to be an instance of werkit.compute.Destination"
            )
        self.destination = destination

        self.runtime_info = runtime_info
        self.handle_exceptions = handle_exceptions
        self.verbose = verbose
        self.time_precision = time_precision
        self.input_message = input_message

    @property
    def message_key(self) -> t.Any:
        try:
            return self.input_message["message_key"]
        except (KeyError, TypeError):
            raise ValueError("Input message is missing `message_key` property")

    @property
    def duration_seconds(self) -> float:
        return round(
            (datetime.datetime.now() - self.start_time).total_seconds(),
            self.time_precision,
        )

    def __enter__(self) -> "Self":
        self.start_time = datetime.datetime.now()
        try:
            self.schema.input_message.validate(self.input_message)
        except:  # noqa: E722
            if not self.__exit__(*sys.exc_info()):
                raise
        return self

    @property
    def result(self) -> t.Any:
        return self._result

    @result.setter
    def result(self, value: t.Any) -> None:
        self.schema.output.validate(value)
        self._result = value

    def serialize_result(self, result: t.Any) -> dict[str, t.Any]:
        return serialize_result(
            message_key=self.message_key,
            serializable_result=result,
            start_time=self.start_time,
            duration_seconds=self.duration_seconds,
            runtime_info=self.runtime_info,
        )

    def _note_compute_success(self, result: t.Any) -> None:
        self.output_message = self.serialize_result(result)
        self.schema.output_message.validate(self.output_message)
        if self.destination:
            self.destination.send(
                message_key=self.message_key, output_message=self.output_message
            )

    def serialize_exception(self, exception: BaseException) -> dict[str, t.Any]:
        return serialize_exception(
            message_key=self.message_key,
            exception=exception,
            error_origin="compute",
            start_time=self.start_time,
            duration_seconds=self.duration_seconds,
            runtime_info=self.runtime_info,
        )

    def _note_compute_exception(self, exception: BaseException) -> bool:
        """
        Return a value suitable for returning from `__exit__`.
        """
        self.output_message = self.serialize_exception(exception)
        self.schema.output_message.validate(self.output_message)
        if self.handle_exceptions:
            print(
                "Error handled by werkit. (To disable, invoke `Manager()` with `handle_exceptions=False`.)"
            )
            print("".join(self.output_message["error"]))
            if self.destination:
                self.destination.send(
                    message_key=self.message_key, output_message=self.output_message
                )
            return True
        else:
            return False

    def __exit__(
        self,
        type: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> t.Optional[bool]:
        if type in [KeyboardInterrupt, SystemExit]:
            assert isinstance(value, BaseException)
            raise value
        elif value:
            if self.verbose:
                print(
                    "Errored in {}".format(format_time(self.duration_seconds)),
                    file=sys.stderr,
                )
            return self._note_compute_exception(value)

        # In case of success, make sure the `result` setter has been invoked
        # inside the block.
        try:
            self.result
        except AttributeError:
            return self._note_compute_exception(
                AttributeError("'result' was not set on the 'Manager' instance")
            )

        self._note_compute_success(self.result)

        if self.verbose:
            print(
                "Completed in {}".format(format_time(self.duration_seconds)),
                file=sys.stderr,
            )

        return None
