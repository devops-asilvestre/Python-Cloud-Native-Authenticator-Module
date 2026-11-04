from shared.observability.correlation import (
    CorrelationContext,
    CorrelationId,
    RequestId,
    TraceId,
)
from shared.security.masking import mask_sensitive_data


def test_masking_recurses_without_mutating_input() -> None:
    original = {"password": "secret", "nested": [{"access-token": "token", "label": "safe"}]}

    masked = mask_sensitive_data(original)

    assert masked == {
        "password": "***",
        "nested": [{"access-token": "***", "label": "safe"}],
    }
    assert original["password"] == "secret"


def test_correlation_context_accepts_all_standard_ids() -> None:
    correlation_id = CorrelationId()
    request_id = RequestId()
    trace_id = TraceId()
    context = CorrelationContext(
        correlation_id=correlation_id,
        request_id=request_id,
        trace_id=trace_id,
    )

    assert context.correlation_id == correlation_id
    assert context.request_id == request_id
    assert context.trace_id == trace_id
