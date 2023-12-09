# qcc-gateway-hl7-listener testing

## Setup
The following commands launch the compose stack and configures our NATS Jetstream.

```shell
just start
just status
just add-stream
```

Note: The datadog agent is not included by default. To launch datadog use the `just start-all` recipe to start services and
`just down-all` to remove.

## Execution

The test harness requires a single parameter, a HL7 file path. A set of test files are available in [src/test/resources/hl7_messages](./src/test/resources/hl7_messages).

```shell
just run-test-harness ./src/test/resources/hl7_messages/adt-a01-sample01.hl7
```

Output:
```shell
=========================
starting test harness app with parameters:
hl7_path = ./src/test/resources/hl7_messages/adt-a01-sample01.hl7
mllp_host = localhost
mllp_port = 2575
sending hl7 message ....
received HL7 acknowledgement:
b'\x0bMSH|^~\\&|GHH LAB, INC.|GOOD HEALTH HOSPITAL|ADT1|GOOD HEALTH HOSPITAL|20231209031614||ACK^A01^ACK|3343031614808714QR75|P|2.8\rMSA|AA|MSG00001\r\x1c\r'
=========================
nats str info hl7
Information for Stream hl7 created 2023-12-08 16:29:12

             Subjects: hl7.queue
             Replicas: 1
              Storage: File

Options:

            Retention: Limits
     Acknowledgements: true
       Discard Policy: Old
     Duplicate Window: 2m0s
    Allows Msg Delete: true
         Allows Purge: true
       Allows Rollups: false

Limits:

     Maximum Messages: unlimited
  Maximum Per Subject: unlimited
        Maximum Bytes: unlimited
          Maximum Age: 1y0d0h0m0s
 Maximum Message Size: unlimited
    Maximum Consumers: unlimited


State:

             Messages: 12
                Bytes: 6.3 KiB
             FirstSeq: 1 @ 2023-12-08T21:31:17 UTC
              LastSeq: 12 @ 2023-12-09T03:16:14 UTC
     Active Consumers: 0
   Number of Subjects: 1
```
