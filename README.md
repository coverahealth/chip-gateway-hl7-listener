# gateway-hl7-listener

The gateway-hl7-listener ("hl7-listener") is the "entry-point" for Gateway deployments which support a "solicited" or
"pull" study workflow. In the "pull" study workflow, studies are fetched from a provider network's PACS server using
lookup keys parsed from the provider network's [HL7 v2](https://hl7-definition.caristix.com/v2/) clinical data stream.

The `gateway-hl7-listener` provides a [mllp listener](https://docs.oracle.com/cd/E19509-01/820-5508/ghadt/index.html)
used to consume the triggered events within the data stream. Messages are [acknowledged](https://hl7-definition.caristix.com/v2/HL7v2.5/TriggerEvents/ACK)
as they are processed, to inform the sending client if the message was received, rejected, or failed due to an error.

Valid messages are transmitted to an "outbound" [NATS Jetstream](https://docs.nats.io/nats-concepts/jetstream) subject,
`hl7.queue`. Messages within the `hl7.queue` are picked up and processed by the [Membership Checker](https://github.com/coverahealth/qcc-gateway-membership-checker).

## Setup

### Project Dependencies

* [pyenv](https://github.com/pyenv/pyenv) for Python version management.
* [Python 3.9.9](https://docs.python.org/3.9/) installed as an available pyenv version.
* [nats-cli](https://github.com/nats-io/natscli/blob/main/README.md) for messaging testing.
* [just](https://just.systems/man/en/chapter_5.html) for executing project tasks.
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or equivalent container runtime.
* Configure `ARTIFACTORY_USER` and `ARTIFACTORY_PASSWORD` env variables within the shell.

### Python Version Validation

```shell
pyenv versions
# output should contain 3.9.x
```

### Project Setup

```shell
# configure poetry virtual environment
poetry env use $(which python3)
poetry install --with=dev,test

# run unit tests
just test-coverage

# confirm build process - python wheel and docker container
just build $ARTIFACTORY_USER $ARTIFACTORY_PASSWORD

# confirm service startup and shutdown
just start
just status
just stop
```
