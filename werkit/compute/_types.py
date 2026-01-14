import typing as t
from typing_extensions import TypedDict

MessageKeyType = t.TypeVar("MessageKeyType")
ResultType = t.TypeVar("ResultType")


class WerkitComputeMeta(TypedDict):
    start_time: str
    duration_seconds: float
    runtime_info: t.Optional[t.Any]


class WerkitSuccessOutputMessage(
    WerkitComputeMeta, TypedDict, t.Generic[ResultType, MessageKeyType]
):
    success: t.Literal[True]
    result: ResultType
    error: None
    error_origin: None
    message_key: MessageKeyType


WerkitErrorOrigin = t.Literal["compute", "system", "orchestration"]


class WerkitErrorOutputMessage(WerkitComputeMeta, TypedDict, t.Generic[MessageKeyType]):
    success: t.Literal[False]
    result: None
    error: list[str]
    error_origin: WerkitErrorOrigin
    message_key: MessageKeyType


WerkitOutputMessage = t.Union[
    WerkitSuccessOutputMessage[ResultType, MessageKeyType],
    WerkitErrorOutputMessage[MessageKeyType],
]
