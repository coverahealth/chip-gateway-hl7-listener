# gateway-hl7-listener
This is a Python service that does the following:
* Listen/receive MLLP HL7 messages from the configured port.
* Publish (NATS Publish-Subscribe mode) the received HL7 messages to the configured NATS JetStream server "Subject" (e.g., "HL7.<subject-name>").
Note that the "Subject" is associated with a JetStream "Stream" (e.g., "HL7") and the stream's "Consumer" (e.g.,"MESSAGES").
* The published NATS messages are acknowledge by the server. If messages publishes start to fail or acknowledges do not occur, listening for HL7 messages will halt.

## Development

### Setup

```bash
gradle tasks # will list all the available tasks
gradle build # will setup virtualenv, run all tests, and create reports and distribution
```

Update gradle.properties as needed.

### Adding Dependencies
Update the build.gradle file to add dependencies.
### Install NATS Jetstream server and NATS CLI

You can find the instructions for the NATS Jetstream server (via docker) here:
https://hub.docker.com/_/nats/

You can find the instructions for the NATS Cli here:
https://github.com/nats-io/natscli

### Create the HL7 stream and MESSAGES consumer

Create the HL7 stream with wildcard/unspecified subjects:

```bash
nats str add HL7 --subjects "HL7.*" --ack --max-msgs=-1 --max-bytes=-1 --max-age=1y --storage file --retention limits --max-msg-size=-1 --discard=old --max-msgs-per-subject=-1 --dupe-window=2m --replicas=1
```

Create the MESSAGES consumer for the HL7 stream and filter to a subject named "HL7.MESSAGES":

```bash
nats con add HL7 MESSAGES --filter HL7.MESSAGES --ack explicit --pull --deliver all --max-deliver=-1 --sample 100
```

### Building

Use gradle to do a clean build (for Windows, "clean" is not available from  PowerShell terminal):

```bash
gradle clean build 
```

### Testing

To run unittest, execute:

```bash
gradle clean test 
```

### Environment variables

You will need to override these if you are not running locally.

HL7_MLLP_HOST = HL7 MLLP host server

HL7_MLLP_PORT = HL7 MLLP host server port to listen for incoming HL7 messages

NATS_OUTGOING_SUBJECT = NATS subject to use

NATS_SERVER_URL = NATS Jetstream connection info

### Creating the docker image

Create the container using the docker build command below. Add your artifactory id (this is likely your w3 email) and key where specified.

```bash
docker build -t gateway-hl7-listener:1.0.0 .
```

If the steps completed successfully, the image specified by the -t option should now exist.
