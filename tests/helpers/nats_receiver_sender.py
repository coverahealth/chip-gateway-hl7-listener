"""
Utility to send or receive NATS JetStream messages.

Preconditions:
- Start the NATs docker NATS JetStream server. 

- Stream "HL7", Consumer "MESSAGES", and Subject "HL7.MESSAGES exist
  on the NATS JetStream server.
"""
import os
import argparse
import asyncio
import hl7
from nats.aio.client import Client as NATS

outstanding_nats_acks = 0

_subject = os.getenv("WHPA_CDP_CLIENT_GATEWAY_MESSAGES", default="HL7.MESSAGES")
_nats_server_url = os.getenv(
    "WHPA_CDP_CLIENT_GATEWAY_NATS_SERVER_URL", default="127.0.0.1:4222"
)
_nc = NATS()  # Get the NATS client.

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


# Send push request to the JetStream server subject.
async def sender():
    """ Send push request message (push/pull NATS mode) and handle ACK from Consumer, indicating message was received. """

    global outstanding_nats_acks

    # Send messages to the NATS Subject.
    for filename in _test_hl7_message_filenames:
        msg = str(hl7.parse(get_hl7_message(filename)))

        # Callback to handle the ACK from the Consumer acknowledging the receipt of the message.
        async def ack_from_consumer_handler(msg):
            global outstanding_nats_acks
            data = msg.data.decode()
            print(
                "Received ACK from Consumer acknowledging the receipt of the message. ACK data={data}".format(
                    data=data
                )
            )
            outstanding_nats_acks -= 1

        print("Sending {msg}".format(msg=msg))
        await _nc.request(_subject, msg.encode("utf-8"), cb=ack_from_consumer_handler)
        outstanding_nats_acks += 1

        while outstanding_nats_acks > 2:
            print(
                "!! Potential problem. NATS Consumer is not ack'ing sent messages. Wait..."
            )
            asyncio.sleep(1)


async def receiver():
    """ Receive message via the pull mode (push/pull) and acknowledge receiving the message. """

    # Loop to continuously receive messages.
    while True:
        # Receive a message and send ACK
        async def receive_msg_and_send_ack_handler(msg):
            data = msg.data.decode()
            print("Received NATS message. Data = ", data)

            await _nc.request(msg.reply, b"+ACK")
            print("ACK'd the received message.")

        print("Attempt to receive message from subject = ", _subject)
        _nc.request
        response = await _nc.request(
            "$JS.API.CONSUMER.MSG.NEXT." + _subject,
            payload=b"",
            cb=receive_msg_and_send_ack_handler,
        )
        print("After nc.request to receive message. response = ", response)
        # Delay before checking for another message.
        await asyncio.sleep(2)


async def main(start_receiver: bool, start_sender: bool):
    await _nc.connect(_nats_server_url)

    if start_receiver:
        receiving_task = asyncio.create_task(receiver())
    if start_sender:
        sending_task = asyncio.create_task(sender())

    # Start the tasks.
    if start_receiver:
        await receiving_task
    if start_sender:
        await sending_task

    await _nc.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start the NATS JetStream receiver and/or sender."
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
