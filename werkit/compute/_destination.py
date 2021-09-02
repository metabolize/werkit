from abc import ABC, abstractmethod

class Destination(ABC):
    @abstractmethod
    def send(self, message_key, serialized_result):
        pass
