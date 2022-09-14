"""This HL7 MLLP Listener/Receiver Service will do the following:

1) Connect to the configured HL7 MLLP host and then listen for incoming HL7 messages.
2) Received messages will be sent to the configured NATS JetStream server Subject. If the message sent to the
NATS server fails, the process of listening for incomming HL7 messages will halt.

Preconditions:
- HL7 MLLP host and port are available for use.
- NATS JetStream server is running and configured with expected Subject.
"""
import asyncio
import os

import hl7
from hl7.mllp import start_hl7_server
from hl7_listener import (
    logger_util,
    logging_codes
)
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers


logger = logger_util.get_logger(__name__)

# HL7 is the Stream and ENCRYPTED_BATCHES is the Consumer.
_subject = os.getenv("NATS_OUTGOING_SUBJECT", default="HL7.MESSAGES")
# NATS Jetstream connection info
_nats_server_url = os.getenv("NATS_SERVER_URL")
_hl7_mllp_host = os.getenv("HL7_MLLP_HOST")
_hl7_mllp_port = os.getenv("HL7_MLLP_PORT")

logger.info(
    logging_codes.STARTUP_ENV_VARS,
    _hl7_mllp_host,
    _hl7_mllp_port,
    _nats_server_url,
    _subject
)
_nc = None  # NATS Client


async def send_msg_to_nats(msg):
    """Synchronously (no callback or async ACK) send the input message to the NATS
    configured Subject.

    Note: An Exception will result if the send times out or fails for other reasons.
    """
    logger.info(logging_codes.SENDING_MSG_TO_NATS)
    send_response = await _nc.request(_subject, msg, timeout=10, cb=None)
    logger.info(logging_codes.NATS_REQUEST_SEND_MSG_RESPONSE, send_response)


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

            await send_msg_to_nats(str(hl7_message).encode("utf-8"))

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
            host=_hl7_mllp_host,
            port=int(_hl7_mllp_port),
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


async def nc_connect() -> bool:
    """Connect to the NATS jetstream server."""
    global _nc
    _nc = NATS()
    try:
        await _nc.connect(_nats_server_url)
        logger.info(logging_codes.NATS_CONNECTED, _nats_server_url)
        return True
    except ErrNoServers as exp:
        logger.error(logging_codes.NATS_CONNECT_ERROR, exc_info=exp)
        raise exp


async def main():
    global _nc
    await nc_connect()  # Create a NATS client connection.
    await hl7_receiver()  # Listen/receive HL7 messages.
    if _nc:
        await _nc.close()  # Needed to avoid exception when program ends.


if __name__ == "__main__":
    asyncio.run(main())
