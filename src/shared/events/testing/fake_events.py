"""Small typed event fixtures for tests and examples."""

from pydantic import BaseModel, ConfigDict, Field

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.metadata.event_metadata import EventMetadata
from shared.events.metadata.event_version import EventVersion
from shared.events.registry.event_registry import EventRegistry


class FakeUserCreatedPayload(BaseModel):
    """Safe example schema for a user-created integration event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    user_id: str = Field(min_length=1)


FAKE_EVENT_TYPE = "identity.user.created"
FAKE_EVENT_VERSION = EventVersion(major=1)


def make_fake_user_created_event(
    *,
    tenant_id: str = "tenant-test",
    source_service: str = "identity-directory-service",
    user_id: str = "user-test",
) -> EventEnvelope:
    """Create a deterministic-shape example envelope with generated IDs."""

    metadata = EventMetadata(tenant_id=tenant_id, source_service=source_service)
    return EventEnvelope.from_metadata(
        event_type=FAKE_EVENT_TYPE,
        event_version=FAKE_EVENT_VERSION,
        metadata=metadata,
        payload={"user_id": user_id},
    )


def make_fake_event_registry() -> EventRegistry:
    """Return a registry containing the fake user-created schema."""

    registry = EventRegistry()
    registry.register(FAKE_EVENT_TYPE, FAKE_EVENT_VERSION, FakeUserCreatedPayload)
    return registry
