import typing as t

from werkit.compute import Destination

if t.TYPE_CHECKING:
    from mypy_boto3_lambda.client import LambdaClient

_lambda_client = None


def get_lambda_client() -> "LambdaClient":
    import boto3

    global _lambda_client
    if not _lambda_client:  # pragma: no cover
        _lambda_client = boto3.client("lambda")

    return _lambda_client


class LambdaDestination(Destination):
    def __init__(
        self,
        task_identifier: t.Optional[str] = None,
        function_name: t.Optional[str] = None,
        qualifier: t.Optional[str] = None,
    ):
        self.task_identifier = task_identifier
        self.function_name = function_name
        self.qualifier = qualifier

    def send(self, message_key: t.Any, output_message: t.Any) -> None:
        from missouri import json
        import os

        task_identifier = self.task_identifier or os.environ.get(
            "DESTINATION_LAMBDA_TASK_IDENTIFIER", None
        )
        if task_identifier is None:
            raise ValueError(
                "Either DESTINATION_LAMBDA_TASK_IDENTIFIER must be set or task_identifier must be provided"
            )

        function_name = self.function_name or os.environ.get(
            "DESTINATION_LAMBDA_FUNCTION_NAME", None
        )
        if function_name is None:
            raise ValueError(
                "Either DESTINATION_LAMBDA_FUNCTION_NAME must be set or function_name must be provided"
            )

        qualifier = self.qualifier or os.environ.get(
            "DESTINATION_LAMBDA_QUALIFIER", None
        )

        # Keep this in sync with the DestinationMessage interface.
        message = {"taskIdentifier": self.task_identifier, "payload": output_message}

        # TODO: Dry this while satisfying the type checker...
        if qualifier is None:
            get_lambda_client().invoke(
                FunctionName=function_name,
                InvocationType="Event",
                Payload=json.dumps(message),
            )
        else:
            get_lambda_client().invoke(
                FunctionName=function_name,
                InvocationType="Event",
                Payload=json.dumps(message),
                Qualifier=qualifier,
            )
