"""Audit event captured for EventBridge publication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Minimal audit record; payload content is never recorded."""

    event_id: str
    event_type: str
    version: str
    tenant_id: str
    publisher: str
    timestamp: datetime
    correlation_id: str
    trace_id: str

    @classmethod
    def from_event(
        cls,
        *,
        event_id: str,
        event_type: str,
        version: str,
        tenant_id: str,
        publisher: str,
        correlation_id: str,
        trace_id: str,
    ) -> AuditRecord:
        return cls(
            event_id=event_id,
            event_type=event_type,
            version=version,
            tenant_id=tenant_id,
            publisher=publisher,
            timestamp=datetime.now(UTC),
            correlation_id=correlation_id,
            trace_id=trace_id,
        )
