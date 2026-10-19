"""Correlation identifiers for request and trace propagation."""

from dataclasses import dataclass
from typing import NewType

CorrelationId = NewType("CorrelationId", str)
RequestId = NewType("RequestId", str)
TraceId = NewType("TraceId", str)


@dataclass(frozen=True, slots=True)
class CorrelationContext:
    """Optional identifiers carried across process and service boundaries."""

    correlation_id: CorrelationId | None = None
    request_id: RequestId | None = None
    trace_id: TraceId | None = None
