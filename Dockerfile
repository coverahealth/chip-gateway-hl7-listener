FROM python:3.9-slim-buster

COPY dist/*.whl /tmp/files/

RUN pip3 install /tmp/files/*.whl
RUN rm -rf /tmp/files

CMD ["python3", "-m", "hl7_listener.main"]
