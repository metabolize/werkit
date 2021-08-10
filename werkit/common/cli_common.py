from collections import namedtuple

InferredFunctionEnvironment = namedtuple(
    "InferredFunctionEnvironment",
    [
        "function_name",
        "version",
        "sha1",
    ],
)


def infer_function_environment_from_ci_environment():
    import os
    import re

    # CircleCI is supported though contributions are welcome for other CI's.
    tag = os.environ["CIRCLE_TAG"]

    match = re.search(r"([a-z0-9-]+)@([0-9]+\.[0-9]+\.[0-9]+)$", tag)
    if not match:
        raise ValueError(
            f'Malformed tag: {tag} (expected e.g. "my-lambda-function@1.2.3")'
        )
    function_name, version = match.groups()

    return InferredFunctionEnvironment(
        function_name=function_name,
        version=version,
        sha1=None,
    )


def infer_commit_from_ci_environment(function_name):
    import os

    sha1 = os.environ["CIRCLE_SHA1"]

    return InferredFunctionEnvironment(
        function_name=function_name,
        version=None,
        sha1=sha1,
    )
