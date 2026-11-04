"""Reusable construction helpers for event tests."""

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.metadata.event_metadata import EventMetadata
from shared.events.metadata.event_version import EventVersion


def make_event(
    *,
    event_type: str = "identity.user.created",
    event_version: EventVersion | None = None,
    tenant_id: str = "tenant-test",
    source_service: str = "test-service",
    payload: dict[str, object] | None = None,
) -> EventEnvelope:
    """Build a valid envelope with realistic metadata for unit tests."""

    return EventEnvelope.from_metadata(
        event_type=event_type,
        event_version=event_version or EventVersion(major=1),
        metadata=EventMetadata(tenant_id=tenant_id, source_service=source_service),
        payload=payload if payload is not None else {"user_id": "user-test"},
    )
