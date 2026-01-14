"""
Werkit's compute wrapper provides a structured, framework-agnostic execution
environment for running any Python code and validating its result using
[1schema][] (or plain JSON Schema). It automatically catches and serializes
errors, too.

By plugging in a werkit.compute.Destination object, you can upon completion send
the result to a queue (or any other destination, such at S3).

[1schema]: https://github.com/metabolize/1schema/
"""

from ._destination import Destination  # noqa: F401
from ._manager import Manager  # noqa: F401
from ._schema import Schema  # noqa: F401
from ._synthetic_error import SyntheticError  # noqa: F401
from ._types import (  # noqa: F401
    WerkitComputeMeta,
    WerkitErrorOrigin,
    WerkitErrorOutputMessage,
    WerkitOutputMessage,
    WerkitSuccessOutputMessage,
)
