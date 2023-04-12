"""This HL7 MLLP Listener/Receiver Service will do the following:

1) Connect to the configured HL7 MLLP host and then listen for incoming HL7 messages.
2) Received messages will be sent to the configured NATS JetStream server Subject. If the message sent to the
NATS server fails, the process of listening for incomming HL7 messages will halt.

Preconditions:
- HL7 MLLP host and port are available for use.
- NATS JetStream server is running and configured with expected Subject.
"""
import asyncio
import json

import hl7
from hl7.mllp import start_hl7_server

from covera_ddtrace import inject_ddtrace
from hl7_listener.utils import (
    logger_util,
    logging_codes
)
from hl7_listener.settings import settings
from hl7_listener.messaging.settings import (
    settings as messager_settings,
    messager
)

from hl7_listener.healthcheck import start_health_check_server


logger = logger_util.get_logger(__name__)


@inject_ddtrace
async def process_received_hl7_messages(hl7_reader, hl7_writer):
    """This will be called every time a socket connects to the receiver/listener."""
    peername = hl7_writer.get_extra_info("peername")
    logger.info(logging_codes.HL7_MLLP_CONNECTED, peername)
    try:
        # Note: IncompleteReadError can occur if the HL7 message sender ends and fails to
        # close its writer (reader for this function). It results in a empty byte buffer (b'') which
        # causes the IncompleteReadError. This function's hl7_reader.at_eof() will
        # then be True.
        hl7_message = None
        while not hl7_reader.at_eof():
            hl7_message = await hl7_reader.readmessage()
            logger.info(logging_codes.HL7_MLLP_MSG_RECEIVED)
            # This may not be needed since the hl7_mllp sender should fail if the message
            # was not valid hl7 message.
            hl7.parse(str(hl7_message))

            await messager.send_msg(msg=str(hl7_message))

            # Send ACK to acknowledge receipt of the message.
            hl7_writer.writemessage(hl7_message.create_ack())
            # The drain() will fail if the hl7 sender does not process the ACK.
            await hl7_writer.drain()
    except hl7.exceptions.ParseException as exp:
        logger.error(logging_codes.HL7_MLLP_MSG_PARSE_ERR, peername, exc_info=exp)
        # Send ack code Application Reject (AR).
        hl7_writer.writemessage(hl7_message.create_ack(ack_code="AR"))
    except asyncio.IncompleteReadError as exp:
        if hl7_reader.at_eof():
            logger.info(logging_codes.HL7_MLLP_CONNECTION_CLOSING, peername)
        else:
            # Unexpected error.
            logger.error(logging_codes.HL7_MLLP_INCOMPLETE_READ, peername, exc_info=exp)
            if hl7_message:
                # Send ack code Application Error (AE).
                hl7_writer.writemessage(hl7_message.create_ack(ack_code="AE"))
            else:
                raise exp
    except Exception as exp:
        logger.error(logging_codes.HL7_MLLP_UNKNOWN_ERR, peername, exc_info=exp)
        if hl7_message:
            # Send ack code Application Error (AE).
            hl7_writer.writemessage(hl7_message.create_ack(ack_code="AE"))
        else:
            raise exp
    finally:
        if hl7_writer:
            hl7_writer.close()
            await hl7_writer.wait_closed()
        # Note: the message sender will close the hl7_reader (writer from the
        # sender perspective).
        logger.info(logging_codes.HL7_MLLP_DISCONNECTED, peername)


async def hl7_receiver():
    """Receive HL7 MLLP messages on the configured host and port."""
    try:
        async with await start_hl7_server(
            process_received_hl7_messages,  # Callback function.
            host=settings.HL7_MLLP_HOST,
            port=int(settings.HL7_MLLP_PORT),
        ) as hl7_server:
            # Listen forever or until a cancel occurs.
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        # Cancel errors are expected.
        logger.info(logging_codes.HL7_MLLP_RECEIVER_CANCELLED)
        pass
    except Exception as exp:
        logger.error(logging_codes.HL7_MLLP_RECEIVER_ERR, exc_info=exp)
        raise exp


async def main():
    logger.info(
        logging_codes.STARTUP_ENV_VARS,
        json.dumps({
            "settings": settings.dict(),
            "messager_settings": messager_settings.dict()
        })
    )
    await messager.connect()
    asyncio.create_task(hl7_receiver())
    await start_health_check_server()
    await asyncio.Event().wait()
    if messager.conn and hasattr(messager.conn, "close"):
        await messager.conn.close()


if __name__ == "__main__":
    asyncio.run(main())
