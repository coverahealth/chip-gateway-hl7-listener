"""Test helper that will send hl7 MLLP messages to the configured HLL7 receiver."""

"""
Test helper that will send hl7 MLLP messages to the configured HLL7 receiver.

Preconditions:
- The HL7 MLLP receiver must be running before the sender is started.
"""
import argparse
import os
import asyncio

import hl7
from hl7.mllp import open_hl7_connection
from hl7.mllp import start_hl7_server

# Get MLLP HL7 HOST IP.
hl7_host = os.getenv("WHPA_CDP_CLIENT_GATEWAY_MLLP_HL7_HOST", "127.0.0.1")
# Get MLLP HL7 host server port to listen for incoming HL7 messages
hl7_port = os.getenv("WHPA_CDP_CLIENT_GATEWAY_MLLP_HL7_PORT", "2575")
# Get timezone
timezone = os.getenv("WHPA_CDP_CLIENT_GATEWAY_TIMEZONE", default="America/New_York")


_hl7_messages_relative_dir = "./tests/resources/hl7_messages/"
_test_hl7_message_filenames = [
    "adt-a01-sample01.hl7",
    "adt-a01-sample04.hl7",
    "oru-r01-sample01.hl7",
    "oru-r01-sample06.hl7",
]


def get_hl7_message(filename: str) -> str:
    """Return the HL7 message string."""
    with open(_hl7_messages_relative_dir + filename, "r") as file:
        return str(file.read())


async def process_received_hl7_messages(hl7_reader, hl7_writer):
    """This will be called every time a socket connects to the receiver/listener. """
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")
    try:
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            print(f"Receiver received message\n{hl7_message}".replace("\r", "\n"))

            # Now let's send the ACK to the message sender and wait for the writer/sender to drain it.
            print("Receiver sending the message ack...")
            # Noteif the sender times out, the hl7_writer.drain() will fail.
            hl7_writer.writemessage(hl7_message.create_ack())
            # The drain() will fail if the hl7 sender does not receive or handle the ack.
            await hl7_writer.drain()
    except asyncio.IncompleteReadError:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    print(f"Connection closed {peername}")


async def hl7_receiver():
    try:
        print("In start of the hl7 MLLP listener/receiver.")
        async with await start_hl7_server(
            process_received_hl7_messages,  # Call back function.
            host=hl7_host,
            port=hl7_port,
        ) as hl7_server:
            # Listen forever or until a cancel occurs.
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        # Cancelled errors are expected
        pass
    except Exception:
        print("Error occurred in hl7_receiver!")


async def hl7_sender():
    """Send an HL7 message to the receiver/listener. The listener needs to be active."""

    # Open the connection to the HL7 receiver. Using wait_for is optional, but recommended so
    # a dead receiver won't block you for long
    hl7_reader, hl7_writer = await asyncio.wait_for(
        open_hl7_connection(hl7_host, int(hl7_port)), timeout=10,
    )

    # Send messages to the receiver/listener.
    for filename in _test_hl7_message_filenames:
        message = get_hl7_message(filename)
        hl7_message = hl7.parse(message)

        # Write the message to the hl7 listner host and port.
        hl7_writer.writemessage(hl7_message)
        # drain() waits for the writemessage to actually complete.
        await hl7_writer.drain()
        print(f"Sent message\n {hl7_message}".replace("\r", "\n"))

        print("Waiting for the HL7 listener to acknowledge the sent message...")
        # If timeout occurs, the
        hl7_ack = await asyncio.wait_for(hl7_reader.readmessage(), timeout=10)
        print(f"Sender received ACK\n {hl7_ack}".replace("\r", "\n"))
    hl7_writer.close()
    # Note: listener will close the hl7_reader (which is the writer from the listner perspective).


async def main(start_receiver: bool, start_sender: bool):
    # Create tasks to run concurrently in the asyncio loop.

    if start_receiver:
        hl7_receiver_task = asyncio.create_task(hl7_receiver())

    if start_sender:
        hl7_sender_task = asyncio.create_task(hl7_sender())

    # If specified, the receiver task must start before the sender.
    if start_receiver:
        await hl7_receiver_task

    if start_sender:
        await hl7_sender_task


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start the MLLP HL7 receiver and/or sender."
    )
    parser.add_argument(
        "--start-receiver",
        default=False,
        action="store_true",
        help="Start the receiver task.",
    )
    parser.add_argument(
        "--start-sender",
        default=False,
        action="store_true",
        help="Start the sender task. The receiver needs to be running already or '--start-receiver' specified.",
    )
    args = parser.parse_args()

    asyncio.run(main(args.start_receiver, args.start_sender))
