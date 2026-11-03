from __future__ import annotations

from typing import Protocol

from identity_service.domain.entities import User
from identity_service.domain.events import UserDomainEvent
from shared.eventbus.models.publish_result import PublishResult
from shared.events import EventContext, EventEnvelope
from shared.events.metadata.event_version import EventVersion


class EventBridgePort(Protocol):
    def publish(self, event: EventEnvelope) -> PublishResult: ...


class IdentityEventBridgePublisher:
    """Maps allowlisted identity events to the shared EventBridge contract."""

    def __init__(self, publisher: EventBridgePort) -> None:
        self.publisher = publisher

    async def publish(self, event: UserDomainEvent, user: User) -> None:
        event_type = f"identity.user.{event.event_type.removeprefix('User').lower()}"
        envelope = EventEnvelope.from_domain_event(
            event,
            event_type=event_type,
            event_version=EventVersion.parse("1.0.0"),
            context=EventContext(tenant_id=user.tenant_id),
            source_service="identity-directory-service",
            payload={"user_id": str(user.user_id), "tenant_id": user.tenant_id},
        )
        self.publisher.publish(envelope)
