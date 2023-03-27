install:
    poetry install

test:
    poetry run pytest

build artifactory_user artifactory_api_key:
    poetry build -f wheel
    docker build \
     --build-arg ARTIFACTORY_USER={{artifactory_user}} \
     --build-arg ARTIFACTORY_API_KEY={{artifactory_api_key}} \
     -t qcc-gateway-hl7-listener:1.0.0 .

start:
    docker compose -f local/docker-compose.yml up

start-local-process:
    poetry run python -m hl7_listener.main

start-prereq:
    docker compose -f local/docker-compose.yml up nats-js nats-tools

format:
    poetry run sh -c 'autopep8 -a -a -a -i -r . && isort . && docformatter -i -r .'

format-verbose:
    poetry run sh -c 'autopep8 -a -a -a -i -r -v . && isort -v . && docformatter -i -r .'

format-dryrun:
    poetry run sh -c 'autopep8 -a -a -a -d -r . && isort --diff . && docformatter -r .'
