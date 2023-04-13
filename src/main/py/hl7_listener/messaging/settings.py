from pydantic import (
    AnyUrl,
    BaseSettings
)

from hl7_listener.settings import (
    QueueType,
    settings as settings_
)

import hl7_listener.messaging.sqs as _sqs
import hl7_listener.messaging.nats as _nats


class SQSSettings(BaseSettings):
    SQS_OUTBOUND_QUEUE_URL: AnyUrl


class NATSSettings(BaseSettings):
    NATS_OUTGOING_SUBJECT: str = "HL7.MESSAGES"
    NATS_SERVER_URL: str


MESSAGER_CONFIG_MAP = {
    QueueType.NATS: {"settings": NATSSettings, "messager": _nats.NATSMessager},
    QueueType.SQS: {"settings": SQSSettings, "messager": _sqs.SQSMessager}
}


settings = MESSAGER_CONFIG_MAP[settings_.OUTBOUND_QUEUE_TYPE]["settings"]()
messager = MESSAGER_CONFIG_MAP[settings_.OUTBOUND_QUEUE_TYPE]["messager"]()