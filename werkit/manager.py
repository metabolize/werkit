from __future__ import print_function
from traceback import format_exception
import datetime
from .format_time import format_time


class Manager:
    def __init__(self, handle_exceptions=True, verbose=False, precision=0):
        self.handle_exceptions = handle_exceptions
        self.verbose = verbose
        self.precision = precision
        self.result = None

    def __enter__(self):
        self.start_time = datetime.datetime.now()
        return self

    def __exit__(self, type, value, traceback):
        duration = int(
            round(
                (datetime.datetime.now() - self.start_time).total_seconds(),
                self.precision,
            )
        )

        if type in [KeyboardInterrupt, SystemExit]:
            raise value

        if value:
            formatted = format_exception(type, value, traceback)
            self.serialized_result = {
                "success": False,
                "result": None,
                "error": formatted,
                "duration_seconds": duration,
            }
            if self.handle_exceptions:
                print(
                    "Error handled by werkit (to disable, pass `handle_exceptions=False` to werkit.manage_execution)"
                )
                print(traceback)
                return True
            else:
                return False
        else:
            self.serialized_result = {
                "success": True,
                "result": self.result,
                "error": None,
                "duration_seconds": duration,
            }

        if self.verbose:
            print("Completed in {}".format(format_time(duration)))
