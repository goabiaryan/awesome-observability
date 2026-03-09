import os
from typing import Optional
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


class OTLPConfig:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        service_name: Optional[str] = None,
        batch_size: int = 512,
        schedule_delay_millis: int = 5000
    ):
        self.endpoint = endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://localhost:4317"
        )
        self.service_name = service_name or os.getenv(
            "OTEL_SERVICE_NAME",
            "llm-agent-app"
        )
        self.batch_size = batch_size
        self.schedule_delay_millis = schedule_delay_millis
        self.tracer_provider = None

    def initialize(self) -> TracerProvider:
        if self.tracer_provider is not None:
            return self.tracer_provider

        otlp_exporter = OTLPSpanExporter(
            endpoint=self.endpoint,
            insecure=True
        )

        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=self.batch_size,
                schedule_delay_millis=self.schedule_delay_millis
            )
        )

        return self.tracer_provider

    def instrument_fastapi(self, app):
        FastAPIInstrumentor.instrument_app(
            app,
            service_name=self.service_name
        )

    def instrument_requests(self):
        RequestsInstrumentor().instrument()

    def instrument_httpx(self):
        HTTPXClientInstrumentor().instrument()


def setup_otlp_tracing(
    endpoint: Optional[str] = None,
    service_name: Optional[str] = None
) -> OTLPConfig:
    config = OTLPConfig(endpoint=endpoint, service_name=service_name)
    config.initialize()
    return config


def is_otlp_disabled() -> bool:
    return os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true"
