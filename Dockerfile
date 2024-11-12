FROM coverahealth.jfrog.io/development-docker/python-base-image:1.0.0

COPY dist/*.whl /tmp/files/

RUN --mount=type=secret,id=ARTIFACTORY_USER,required \
    --mount=type=secret,id=ARTIFACTORY_API_KEY,required \
    pip3 install --extra-index-url https://$(cat /run/secrets/ARTIFACTORY_USER):$(cat /run/secrets/ARTIFACTORY_API_KEY)@coverahealth.jfrog.io/artifactory/api/pypi/development-pypi/simple /tmp/files/*.whl
RUN rm -rf /tmp/files

CMD ["ddtrace-run", "python3", "-m", "hl7_listener.main"]
