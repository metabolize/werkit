from abc import ABC, abstractmethod
import typing as t


class Destination(ABC):
    @abstractmethod
    def send(
        self, message_key: t.Any, output_message: t.Any
    ) -> None:  # pragma: no cover
        pass
