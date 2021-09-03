from abc import ABC, abstractmethod


class Destination(ABC):
    @abstractmethod
    def send(self, message_key, output_message):  # pragma: no cover
        pass
