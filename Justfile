install:
    poetry install

test *args:
    poetry run pytest {{args}}

test-coverage *args:
    poetry run pytest {{args}} --cov-report term-missing --cov=src/main/py/hl7_listener --cov-fail-under=80 src/test/

build artifactory_user artifactory_api_key *args:
    poetry build -f wheel
    docker build {{args}} \
     --build-arg ARTIFACTORY_USER={{artifactory_user}} \
     --build-arg ARTIFACTORY_API_KEY={{artifactory_api_key}} \
     -t qcc-gateway-hl7-listener:1.0.0 .

restart artifactory_user artifactory_api_key:
    just docker-cleanup
    just build {{artifactory_user}} {{artifactory_api_key}}
    just start


docker-cleanup:
    docker rmi 'qcc-gateway-hl7-listener:1.0.0'

start:
    docker compose up -d

start-all:
    docker compose --profile monitor up -d

down-all:
    docker compose --profile monitor down -v

down:
    docker compose down -v

status:
    docker compose ps

add-stream:
    nats context add -s localhost nats
    nats context select nats
    nats stream add hl7 --subjects "hl7.queue" --ack --max-msgs=-1 --max-bytes=-1 --max-age=1y --storage file --retention limits --max-msg-size=-1 --discard=old --max-msgs-per-subject=-1 --dupe-window=2m --replicas=1 --no-allow-rollup --no-deny-delete --no-deny-purge

start-local-process:
    poetry run python -m hl7_listener.main

run-test-harness file_path:
    poetry run python3 test-harness/app.py {{file_path}}
    nats str info hl7

format:
    poetry run sh -c 'black . && isort . && docformatter -i -r .'

format-verbose:
    poetry run sh -c 'black -v . && isort -v . && docformatter -i -r .'

format-dryrun:
    poetry run sh -c 'black --diff --color . && isort --diff . && docformatter -r .'
