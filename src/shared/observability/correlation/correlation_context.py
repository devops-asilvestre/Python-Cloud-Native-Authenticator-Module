"""Optional identifiers propagated across service boundaries."""

from pydantic import BaseModel, ConfigDict

from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.request_id import RequestId
from shared.observability.correlation.trace_id import TraceId


class CorrelationContext(BaseModel):
    """Correlation identifiers associated with an operation or request."""

    model_config = ConfigDict(frozen=True)

    correlation_id: CorrelationId | None = None
    request_id: RequestId | None = None
    trace_id: TraceId | None = None
