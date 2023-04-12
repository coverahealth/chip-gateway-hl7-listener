from typing import (
    Union,
    Callable,
)

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers

from covera_ddtrace import inject_ddtrace

from hl7_listener.utils import (
    logger_util,
    logging_codes
)
import hl7_listener.messaging.settings as msgr_config
from hl7_listener.messaging.base import MessagingInterface


logger = logger_util.get_logger(__name__)


class NATSMessager(MessagingInterface):

    @inject_ddtrace
    async def connect(self) -> bool:
        """Connect to the NATS jetstream server."""
        self.conn = NATS()
        try:
            await self.conn.connect(msgr_config.settings.NATS_SERVER_URL)
            logger.info(logging_codes.NATS_CONNECTED, msgr_config.settings.NATS_SERVER_URL)
            return True
        except ErrNoServers as exp:
            logger.error(logging_codes.NATS_CONNECT_ERROR, exc_info=exp)
            raise exp

    @inject_ddtrace
    async def send_msg(self, msg: Union[str, bytes], send_as: Callable = bytes) -> None:
        """Synchronously (no callback or async ACK) send the input message to the NATS
        configured Subject.

        Note: An Exception will result if the send times out or fails for other reasons.
        """
        assert send_as in (str, bytes)
        assert isinstance(msg, (str, bytes))

        to_send = msg
        if isinstance(msg, str) and send_as == bytes:
            to_send = msg.encode()

        elif isinstance(msg, bytes) and send_as == str:
            to_send = msg.decode()

        logger.info(logging_codes.SENDING_MSG_TO_NATS)
        send_response = await self.conn.request(
            msgr_config.settings.NATS_OUTGOING_SUBJECT, to_send, timeout=10, cb=None)
        logger.info(logging_codes.NATS_REQUEST_SEND_MSG_RESPONSE, send_response)
