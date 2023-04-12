from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
)


class MessagingInterface(ABC):

    @abstractmethod
    def send_msg(self, msg: Any, send_as: Callable) -> None:
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

