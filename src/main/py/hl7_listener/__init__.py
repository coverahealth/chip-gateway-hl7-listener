"""
Logging messages for the HL7 Listener
"""

# ERROR
NATS_CONNECT_ERROR = "Error connecting to the NATS server"
HL7_MLLP_INCOMPLETE_READ = "HL7 MLLP Unexpected incomplete message read error"
HL7_MLLP_RECEIVER_ERR = "HL7 MLLP Receiver encountered exception"
HL7_MLLP_MSG_PARSE_ERR = "Received HL7 message is not a valid"
HL7_MLLP_UNKNOWN_ERR = "Unknown error during HL7 receive message processing"

# INFO
STARTUP_ENV_VARS = "HL7 Listener started"
HL7_MLLP_CONNECTED = "HL7 Listener connection established"
HL7_MLLP_MSG_RECEIVED = "HL7 Listener received a message"
HL7_MLLP_DISCONNECTED = "HL7 Listener connection closed"
HL7_MLLP_RECEIVER_CANCELLED = "HL7 Listener was cancelled. This is not considered an error"
NATS_CONNECTED = "Connected to the NATS server URL"
SENDING_MSG_TO_NATS = "Sending message to the NATS JetStream server."
NATS_REQUEST_SEND_MSG_RESPONSE = "Response from NATS request for sending an HL7 message"
SENDING_MSG_TO_SQS = "Sending message to SQS"
SENT_MSG_TO_SQS = "Sent message to SQS"
HL7_MLLP_CONNECTION_CLOSING = "HL7 Listener connection from a sender peer is closing"