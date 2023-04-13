import json

from ddtrace import tracer
from ddtrace.propagation.http import HTTPPropagator


def inject_dd_context(trace: str):
    dd_context = HTTPPropagator.extract(json.loads(trace))
    tracer.context_provider.activate(dd_context)


def extract_dd_context() -> str:
    header_dict = {}
    if current_context := tracer.current_trace_context():
        HTTPPropagator.inject(current_context, header_dict)
    return json.dumps(header_dict)
