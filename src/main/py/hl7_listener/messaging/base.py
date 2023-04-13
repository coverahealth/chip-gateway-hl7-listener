from abc import ABC, abstractmethod
from typing import Any


class MessagingInterface(ABC):

    @abstractmethod
    def send_msg(self, msg: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

