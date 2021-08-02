"""
This HL7 MLLP Listener/Receiver Service will do the following:
1) Connect to the configured HL7 MLLP host and then listen for incoming HL7 messages.
2) Received messages will be sent to the configured NATS JetStream server Subject. If the message
   send to the NATS server fails, the process of listening for incomming HL7 messages will halt.

Preconditions:
- HL7 MLLP host and port are available for use.
- NATS JetStream server is running and configured with expected Subject.
"""
import asyncio
import os
from whpa_cdp_hl7_listener_service import logger_util, logging_codes
from hl7.mllp import start_hl7_server
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrNoServers
from async_retrying import retry
from functools import partial

logger = logger_util.get_logger(__name__)

# HL7 is the Stream and ENCRYPTED_BATCHES is the Consumer.
_subject = os.getenv(
    "WHPA_CDP_CLIENT_GATEWAY_ENCRYPTED_BATCHES", default="HL7.ENCRYPTED_BATCHES"
)
# NATS Jetstream connection info
_nats_server_url = os.getenv(
    "WHPA_CDP_CLIENT_GATEWAY_NATS_SERVER_URL", default="127.0.0.1:4222"
)
_hl7_mllp_host = os.getenv(
    "WHPA_CDP_CLIENT_GATEWAY_HL7_MLLP_HOST", default="127.0.0.1",
)
_hl7_mllp_port = int(
    os.getenv("WHPA_CDP_CLIENT_GATEWAY_HL7_MLLP_PORT", default="2575",)
)
# TODO: Currently timezone and tenant are not used--do they need to be added to NATS message/header?
_timezone = os.getenv("WHPA_CDP_CLIENT_GATEWAY_TIMEZONE", default="America/New_York")
_tenant = os.getenv("WHPA_CDP_CLIENT_GATEWAY_TENANT", default="cloud1")

logger.info(
    logging_codes.STARTUP_ENV_VARS.format(
        _hl7_mllp_host, _hl7_mllp_port, _nats_server_url, _subject, _timezone, _tenant
    )
)

_nc = None  # NATS Client

# The number of outstanding NATS Consumer acknowledgements waiting to be received.
outstanding_nats_acks = 0


async def send_msg_to_nats(msg):
    """
    Send the input message to the NATS configured Subject and wait for the NATS
    Consumer to acknowledge receipt of the message.
    """
    global outstanding_nats_acks

    # Define callback function to process the NATS consumer ACK.
    async def handle_consumer_msg_received_ack(msg):
        global outstanding_nats_acks
        data = msg.data.decode()
        logger.info(logging_codes.NATS_RECEIVED_CONSUMER_ACK.format(data))
        outstanding_nats_acks -= 1

    logger.info(logging_codes.SENDING_MSG_TO_NATS)
    # Note: The NATS streaming server sends ACKs back to the message producers.
    await _nc.request(_subject, msg, cb=handle_consumer_msg_received_ack)
    outstanding_nats_acks += 1
    # Wait for NATS Consumer message ACKs, if needed.
    while outstanding_nats_acks > 2:
        logger.warn(logging_codes.WAITING_ON_NATS_ACKS)
        asyncio.sleep(1)


async def process_received_hl7_messages(hl7_reader, hl7_writer):
    """ This will be called every time a socket connects to the receiver/listener. """
    peername = hl7_writer.get_extra_info("peername")
    logger.info(logging_codes.HL7_MLLP_CONNECTED.format(peername))
    try:
        # Note: IncompleteReadError can occur if the HL7 message sender ends and fails to
        # close its writer (reader for this function). It results in a empty byte buffer (b'') which
        # causes the IncompleteReadError. This function's hl7_reader.at_eof() will then be True.
        while not hl7_reader.at_eof():
            hl7_message = await hl7_reader.readmessage()
            logger.info(logging_codes.HL7_MLLP_MSG_RECEIVED)

            await send_msg_to_nats(str(hl7_message).encode("utf-8"))

            # Send ACK to acknowledge receipt of the message.
            hl7_writer.writemessage(hl7_message.create_ack())
            # The drain() will fail if the hl7 sender does not process the ACK.
            await hl7_writer.drain()

    except asyncio.IncompleteReadError as exp:
        if hl7_reader.at_eof():
            logger.info(logging_codes.HL7_MLLP_CONNECTION_CLOSING.format(peername))
        else:
            # Unexpected error.
            logger.error(logging_codes.HL7_MLLP_INCOMPLETE_READ.format(peername), exp)
            hl7_writer.close()
            # Note: the message sender will close the hl7_reader (writer from the sender perspective).
    logger.info(logging_codes.HL7_MLLP_DISCONNECTED.format(peername))


async def hl7_receiver():
    """ Receive HL7 MLLP messages on the configured host and port."""
    try:
        async with await start_hl7_server(
            process_received_hl7_messages,  # Call back function.
            host=_hl7_mllp_host,
            port=_hl7_mllp_port,
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


async def nc_connect():
    """ Connect to the NATS jetstream server"""
    global _nc
    _nc = NATS()
    try:
        await _nc.connect(_nats_server_url)
        logger.info(logging_codes.NATS_CONNECTED.format(_nats_server_url))
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
