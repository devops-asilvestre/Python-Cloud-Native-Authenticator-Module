"""Unit tests for the shared observability foundation."""

from __future__ import annotations

import uuid

from shared.observability.context.request_context import RequestContext
from shared.observability.context.telemetry_context import TelemetryContext
from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.request_id import RequestId
from shared.observability.correlation.trace_id import TraceId
from shared.observability.exceptions.observability_exception import TelemetryException
from shared.observability.logging.structured_log_entry import StructuredLogEntry
from shared.observability.logging.structured_logger import StructuredLogger
from shared.observability.metrics.counter_contract import CounterContract
from shared.observability.metrics.gauge_contract import GaugeContract
from shared.observability.metrics.histogram_contract import HistogramContract
from shared.observability.tracing.trace_context import TraceContext


def test_correlation_id_is_uuidv7() -> None:
    value = CorrelationId()
    parsed = uuid.UUID(str(value))
    assert parsed.version == 7
    assert isinstance(value, str)


def test_request_and_trace_ids_are_generated() -> None:
    request_id = RequestId()
    trace_id = TraceId()
    assert uuid.UUID(str(request_id)).version == 7
    assert uuid.UUID(str(trace_id)).version == 7


def test_request_context_contains_correlated_metadata() -> None:
    context = RequestContext(tenant_id="tenant-1", user_id="user-42")
    assert str(context.request_id)
    assert str(context.correlation_id)
    assert str(context.trace_id)
    assert context.tenant_id == "tenant-1"
    assert context.user_id == "user-42"


def test_telemetry_context_serializes_for_logs() -> None:
    context = TelemetryContext(
        service_name="auth-service",
        environment="test",
        metadata={"env": "dev"},
    )
    payload = context.to_log_fields()
    assert payload["service_name"] == "auth-service"
    assert payload["environment"] == "test"


def test_structured_log_entry_redacts_sensitive_fields() -> None:
    entry = StructuredLogEntry(
        event="login",
        message="login",
        attributes={"password": "top-secret", "user_id": "42"},
    )
    sanitized = entry.sanitize()
    assert sanitized.attributes["password"] == "[REDACTED]"
    assert sanitized.attributes["user_id"] == "42"


def test_structured_logger_captures_context() -> None:
    logger = StructuredLogger(
        "auth-service",
        request_context=RequestContext(),
        telemetry_context=TelemetryContext(service_name="auth-service"),
    )
    logger.info("user.login", user_id="42", password="secret")
    assert logger.name == "auth-service"


def test_metric_contract_names_are_present() -> None:
    assert CounterContract.__annotations__["name"] is str
    assert GaugeContract.__annotations__["name"] is str
    assert HistogramContract.__annotations__["name"] is str


def test_trace_context_propagates_headers() -> None:
    context = TraceContext()
    headers = context.to_headers()
    assert "x-trace-id" in headers
    assert "x-span-id" in headers
    assert headers["x-trace-id"] == str(context.trace_id)


def test_telemetry_exception_has_code() -> None:
    exc = TelemetryException("bad trace", code="E_TELEMETRY")
    assert str(exc) == "[E_TELEMETRY] bad trace"


def test_request_context_to_log_fields_uses_strings() -> None:
    context = RequestContext()
    log_fields = context.to_log_fields()
    assert isinstance(log_fields["request_id"], str)
    assert isinstance(log_fields["correlation_id"], str)
    assert isinstance(log_fields["trace_id"], str)
