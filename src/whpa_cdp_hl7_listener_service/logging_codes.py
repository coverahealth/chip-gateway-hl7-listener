""" Common place to document project logging codes. HL7L = HL7 Listener service."""

# ERROR

HL7_MLLP_CONNECT_ERROR = "HL7LERR001: Error connecting to the HL7 MLLP listener port {}"
NATS_CONNECT_ERROR = "HL7LERR002: Error connecting to the NATS server {}"
NATS_NOT_INITIALIZED = "HL7LERR003: NATS not initialized."
HL7_MLLP_INCOMPLETE_READ = (
    "HL7LERR004: HL7 MLLP Unexpected incomplete message read error. peername={}"
)
HL7_MLLP_RECEIVER_ERR = "HL7LERR005: HL7 MLLP Receiver encounterred exception."
TEST = "HL7LERR00n: ... "

# WARN
WAITING_ON_NATS_ACKS = "Potential problem: Waiting for message ACKs from NATS Consumer."

# INFO

STARTUP_ENV_VARS = (
    "HL7LLOG001: HL7 Listener started with the follow values from the env:\n"
    + '  HL7 MLLP listening host:port="{}:{}"\n'
    + '  NATs Jetstream Connection="{}" and Subject="{}"\n'
    + '  Timezone="{}", Tenant="{}"'
)
HL7_MLLP_CONNECTED = "HL7LLOG002: HL7 Listener connection established. peername={}"
HL7_MLLP_MSG_RECEIVED = "HL7LLOG003: HL7 Listener received a message."
HL7_MLLP_DISCONNECTED = "HL7LLOG004: HL7 Listener connection closed. peername={}"
HL7_MLLP_RECEIVER_CANCELLED = (
    "HL7LLOG005: HL7 Listener was cancelled. This is not considered an error."
)
NATS_CONNECTED = "HL7LLOG006: Connected to the NATS server URL {}."
SENDING_MSG_TO_NATS = "HL7LLOG007: Sending message to the NATS JetStream server."
NATS_RECEIVED_CONSUMER_ACK = (
    "HL7LLOG008: Received ACK from NATS Consumer for the sent message {}"
)
HL7_MLLP_CONNECTION_CLOSING = (
    "HL7LLOG008: HL7 Listener connection from a sender peer is closing. peername={}"
)
TEST = "HL7LLOG003: ..."
