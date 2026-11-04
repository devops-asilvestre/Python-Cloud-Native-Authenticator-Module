"""Validate event envelopes prior to publication."""

from __future__ import annotations

from shared.eventbus.exceptions.eventbridge_exception import EventValidationException
from shared.eventbus.schema.event_contract_schema import EventContractSchema
from shared.events import EventEnvelope


class EventSchemaEnforcer:
    """Validate required EventBridge envelope guarantees."""

    def validate(self, event: object) -> EventEnvelope:
        if not isinstance(event, EventEnvelope):
            raise EventValidationException("Event envelope is invalid.")
        EventContractSchema(
            event_type=event.event_type,
            version=str(event.event_version),
        ).validate(
            tenant_id=event.tenant_id,
            correlation_id=str(event.correlation_id),
            trace_id=str(event.trace_id),
        )
        return event

    def validate_schema(self, event: EventEnvelope) -> EventEnvelope:
        return self.validate(event)

    def validate_version(self, event: EventEnvelope) -> EventEnvelope:
        self.validate(event)
        return event

    def validate_tenant(self, event: EventEnvelope) -> EventEnvelope:
        self.validate(event)
        return event

    def enforce(self, event: EventEnvelope) -> EventEnvelope:
        return self.validate(event)
