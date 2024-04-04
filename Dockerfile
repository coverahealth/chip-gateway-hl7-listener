FROM coverahealth.jfrog.io/development-docker/python-base-image:1.0.0

ARG ARTIFACTORY_USER
ARG ARTIFACTORY_API_KEY

COPY dist/*.whl /tmp/files/

RUN pip3 install --extra-index-url https://${ARTIFACTORY_USER}:${ARTIFACTORY_API_KEY}@coverahealth.jfrog.io/artifactory/api/pypi/development-pypi/simple /tmp/files/*.whl
RUN rm -rf /tmp/files

CMD ["ddtrace-run", "python3", "-m", "hl7_listener.main"]
