"""Audit publication attempts without logging sensitive payloads."""

from __future__ import annotations

from shared.eventbus.audit.audit_record import AuditRecord
from shared.events import EventEnvelope


class EventAuditor:
    """Record a sanitized audit record for each EventBridge publication."""

    def __init__(self, publisher: str = "eventbridge-publisher") -> None:
        self.publisher = publisher
        self.records: list[AuditRecord] = []

    def audit(self, event: EventEnvelope) -> AuditRecord:
        record = AuditRecord.from_event(
            event_id=str(event.event_id),
            event_type=event.event_type,
            version=str(event.event_version),
            tenant_id=event.tenant_id,
            publisher=self.publisher,
            correlation_id=str(event.correlation_id),
            trace_id=str(event.trace_id),
        )
        self.records.append(record)
        return record
