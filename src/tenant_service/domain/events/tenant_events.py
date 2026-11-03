from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from tenant_service.domain.value_objects import TenantId


@dataclass(frozen=True, slots=True)
class TenantDomainEvent:
    tenant_id: TenantId
    occurred_at: datetime
    event_id: UUID

    @property
    def event_type(self) -> str:
        return type(self).__name__

    @classmethod
    def for_tenant(cls, tenant_id: TenantId) -> TenantDomainEvent:
        return cls(tenant_id, datetime.now(UTC), uuid4())


@dataclass(frozen=True, slots=True)
class TenantCreated(TenantDomainEvent):
    tenant_code: str = ""
    tenant_slug: str = ""


@dataclass(frozen=True, slots=True)
class TenantUpdated(TenantDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class TenantActivated(TenantDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class TenantDeactivated(TenantDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class TenantSuspended(TenantDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class TenantDeleted(TenantDomainEvent):
    pass
