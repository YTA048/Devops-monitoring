"""
Configuration du tracing distribué OpenTelemetry → Jaeger (via OTLP gRPC).
"""
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME as RES_SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def setup_tracing(service_name: str, jaeger_endpoint: str, app) -> None:
    """Initialise un TracerProvider OTLP qui exporte vers Jaeger."""
    try:
        resource = Resource.create({RES_SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        # Instrumentations automatiques
        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
        LoggingInstrumentor().instrument(set_logging_format=True)

        logger.info("tracing_initialized", extra={"endpoint": jaeger_endpoint})
    except (RuntimeError, OSError) as exc:
        # Jaeger pas encore prêt : on log mais on ne casse pas l'app
        logger.warning("tracing_setup_failed", extra={"error": str(exc)})
