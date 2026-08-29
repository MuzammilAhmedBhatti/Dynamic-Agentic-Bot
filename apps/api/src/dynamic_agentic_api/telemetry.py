from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram

from dynamic_agentic_api.config import Settings

HTTP_REQUESTS = Counter(
    "dynamic_agentic_http_requests_total", "HTTP requests", ("method", "route", "status")
)
HTTP_DURATION = Histogram(
    "dynamic_agentic_http_request_duration_seconds", "HTTP request latency", ("method", "route")
)
AGENT_DURATION = Histogram(
    "dynamic_agentic_agent_duration_seconds",
    "Bounded agent stage latency",
    ("stage", "outcome"),
)
AGENT_USAGE = Counter(
    "dynamic_agentic_agent_usage_total", "Bounded route and persona selections", ("kind", "name")
)


def configure_telemetry(app: FastAPI, settings: Settings) -> None:
    if settings.otel_exporter_otlp_endpoint:
        provider = TracerProvider(
            resource=Resource.create({"service.name": settings.otel_service_name})
        )
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=settings.otel_exporter_otlp_endpoint.rstrip("/") + "/v1/traces"
                )
            )
        )
        trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


@contextmanager
def observed_stage(stage: str) -> Iterator[None]:
    started = perf_counter()
    outcome = "success"
    tracer = trace.get_tracer("dynamic_agentic_api")
    try:
        with tracer.start_as_current_span(stage):
            yield
    except Exception:
        outcome = "error"
        raise
    finally:
        AGENT_DURATION.labels(stage=stage, outcome=outcome).observe(perf_counter() - started)
