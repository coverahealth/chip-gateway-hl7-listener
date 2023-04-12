from typing import (
    Union,
    Callable,
)

from aiobotocore.session import get_session

from covera_ddtrace import inject_ddtrace

from hl7_listener.utils import (
    dd_utils,
    logger_util,
    logging_codes
)
import hl7_listener.messaging.settings as msgr_config
from hl7_listener.messaging.base import MessagingInterface


logger = logger_util.get_logger(__name__)


class SQSMessager(MessagingInterface):
    @inject_ddtrace
    async def connect(self) -> bool:
        """Create an aiobotocore session if we don't have one."""
        self.conn = get_session()

    @inject_ddtrace
    async def send_msg(self, msg: Union[str, bytes], send_as: Callable = str) -> None:
        """Sends a msg to an sqs queue."""
        assert send_as in (str, bytes)
        assert isinstance(msg, (str, bytes))

        to_send = msg
        if isinstance(msg, str) and send_as == bytes:
            to_send = msg.encode()

        elif isinstance(msg, bytes) and send_as == str:
            to_send = msg.decode()

        logger.info(logging_codes.SENDING_MSG_TO_SQS, msgr_config.settings.SQS_OUTBOUND_QUEUE_URL)
        await self.connect()
        async with self.conn.create_client('sqs') as client:
            await client.send_message(
                QueueUrl=msgr_config.settings.SQS_OUTBOUND_QUEUE_URL,
                MessageBody=to_send,
                MessageAttributes={
                    "correlation_id": {
                        "StringValue": dd_utils.extract_dd_context(),
                        "DataType": "String"
                    }
                }
            )
            logger.info(logging_codes.SENT_MSG_TO_SQS)
