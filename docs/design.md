# gateway-hl7-listener design

## Overview
Diagram:
![Gateway Appliance](diagrams/gateway_appliance.png)

The `gateway-hl7-listener` is the entry point for Gateway deployments which support a solicited, or "pull", study
workflow where studies are fetched from the provider network's PACS system using identifiers parsed by the provider's
clinical data stream.

## Processing
The `gateway-hl7-listener` complies with mllp protocol conventions and returns a HL7 acknowledgement
to the provider network's mllp client. Supported acknowledgements include:

- Application Accept (AA) for valid messages processed without error.
- Application Reject (AR) if a message does not conform to general HL7 messaging structures.
- Application Error (AE) if an unexpected error occurs when processing the message.
`
HL7 messages are passed along, without filtering, to the `hl7.queue` NATS subject.