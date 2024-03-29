from typing import (
    Union,
)

from aiobotocore.session import get_session
from covera.loglib import configure_get_logger
from covera_ddtrace import inject_ddtrace

import hl7_listener.messaging.settings as msgr_config
from hl7_listener import SENDING_MSG_TO_SQS, SENT_MSG_TO_SQS
from hl7_listener.messaging.base import MessagingInterface
from hl7_listener.utils import dd_utils

logger = configure_get_logger()

class SQSMessager(MessagingInterface):
    @inject_ddtrace
    async def connect(self):
        """Create an aiobotocore session if we don't have one."""
        self.conn = get_session()

    @inject_ddtrace
    async def send_msg(self, msg: Union[str, bytes]) -> None:
        """Sends a msg to an sqs queue."""
        assert isinstance(msg, (str, bytes))

        to_send = msg
        if isinstance(msg, bytes):
            to_send = msg.decode()

        logger.info(
            SENDING_MSG_TO_SQS,
            logging_code="HL7LLOG009",
            sqs_outbound_queue_url=msgr_config.settings.SQS_OUTBOUND_QUEUE_URL
        )
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
            logger.info(SENT_MSG_TO_SQS, logging_code="HL7LLOG010")
