#!/bin/sh

# Create context
nats context add -s nats-js nats
nats context select nats

# Create Streams
nats str add hl7        --subjects "hl7.*" --ack --max-msgs=-1 \
                        --max-bytes=-1 --max-age=1y --storage file \
                        --retention limits  --max-msg-size=-1 --discard=old \
                        --max-msgs-per-subject=-1 --dupe-window=2m --replicas=1 \
                        --no-allow-rollup --no-deny-delete --no-deny-purge
# Create Consumer
nats con add hl7 queue              --filter hl7.queue --ack explicit --pull \
                                    --deliver all --max-deliver=-1 --sample 100 \
                                    --max-pending=-1 --replay=instant --wait=60s \
                                    --no-headers-only --backoff=none