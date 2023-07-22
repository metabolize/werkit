import typing as t
from abc import ABC, abstractmethod


class Destination(ABC):
    @abstractmethod
    def send(
        self, message_key: t.Any, output_message: t.Any
    ) -> None:  # pragma: no cover
        pass
