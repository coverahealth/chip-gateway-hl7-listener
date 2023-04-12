import logging
import sys

from pythonjsonlogger import jsonlogger

from hl7_listener.settings import settings


_log_format = f"%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s"


def get_sysout_stream_handler(stream):
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(settings.LOG_LEVEL)
    stream_handler.setFormatter(jsonlogger.JsonFormatter(_log_format))
    return stream_handler


def get_logger(name, stream=sys.stdout, level=settings.LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(get_sysout_stream_handler(stream))
    return logger
