from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared.events import EventRegistry, EventVersion

TENANT_EVENT_VERSION = EventVersion(major=1)


class TenantEventPayload(BaseModel):
    """Allowlisted, versioned payload shared by Tenant integration events."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(min_length=1)
    tenant_code: str = Field(min_length=3, max_length=20)
    tenant_slug: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1)


TENANT_EVENT_TYPES = (
    "tenant.tenant.created",
    "tenant.tenant.updated",
    "tenant.tenant.activated",
    "tenant.tenant.deactivated",
    "tenant.tenant.suspended",
    "tenant.tenant.deleted",
)


def build_tenant_event_registry() -> EventRegistry:
    registry = EventRegistry()
    for event_type in TENANT_EVENT_TYPES:
        registry.register(event_type, TENANT_EVENT_VERSION, TenantEventPayload)
    return registry
