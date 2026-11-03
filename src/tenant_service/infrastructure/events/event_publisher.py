from __future__ import annotations

from typing import Protocol

from shared.eventbus.models.publish_result import PublishResult
from shared.events import EventContext, EventEnvelope
from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.events import TenantDomainEvent
from tenant_service.infrastructure.events.tenant_event_contracts import (
    TENANT_EVENT_VERSION,
    build_tenant_event_registry,
)


class EventPublisherPort(Protocol):
    def publish(self, event: EventEnvelope) -> PublishResult: ...


class EventPublisher:
    def __init__(self, publisher: EventPublisherPort | None = None) -> None:
        self.publisher = publisher
        self.registry = build_tenant_event_registry()

    async def publish(self, event: TenantDomainEvent, tenant: Tenant) -> None:
        if self.publisher is None:
            return
        context = EventContext(tenant_id=str(tenant.tenant_id))
        payload: dict[str, object] = {
            "tenant_id": str(tenant.tenant_id),
            "tenant_code": str(tenant.tenant_code),
            "tenant_slug": str(tenant.tenant_slug),
            "status": str(tenant.tenant_status),
        }
        event_type = f"tenant.tenant.{event.event_type.removeprefix('Tenant').lower()}"
        payload_model = self.registry.resolve(event_type, TENANT_EVENT_VERSION)
        validated_payload = payload_model.model_validate(payload)
        envelope = EventEnvelope.from_domain_event(
            event,
            event_type=event_type,
            event_version=TENANT_EVENT_VERSION,
            context=context,
            source_service="tenant-service",
            payload=validated_payload.model_dump(mode="json"),
        )
        self.publisher.publish(envelope)
