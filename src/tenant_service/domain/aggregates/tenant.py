from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from tenant_service.domain.events import (
    TenantActivated,
    TenantCreated,
    TenantDeactivated,
    TenantDeleted,
    TenantDomainEvent,
    TenantSuspended,
    TenantUpdated,
)
from tenant_service.domain.exceptions import TenantDomainError
from tenant_service.domain.value_objects import (
    TenantCode,
    TenantDomain,
    TenantId,
    TenantMetadata,
    TenantName,
    TenantSettings,
    TenantSlug,
    TenantStatus,
    TenantStatusValue,
)


@dataclass(slots=True)
class Tenant:
    tenant_id: TenantId
    tenant_name: TenantName
    tenant_code: TenantCode
    tenant_slug: TenantSlug
    tenant_status: TenantStatus
    settings: TenantSettings
    metadata: TenantMetadata
    domains: tuple[TenantDomain, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[TenantDomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        name: TenantName,
        code: TenantCode,
        slug: TenantSlug,
        settings: TenantSettings,
        metadata: TenantMetadata,
        domains: tuple[TenantDomain, ...] = (),
    ) -> Tenant:
        tenant = cls(
            TenantId.generate(),
            name,
            code,
            slug,
            TenantStatus.pending(),
            settings,
            metadata,
            domains,
        )
        tenant._events.append(
            TenantCreated(tenant.tenant_id, tenant.created_at, uuid4(), str(code), str(slug))
        )
        return tenant

    def update(
        self,
        *,
        name: TenantName | None = None,
        slug: TenantSlug | None = None,
        settings: TenantSettings | None = None,
        metadata: TenantMetadata | None = None,
        domains: tuple[TenantDomain, ...] | None = None,
    ) -> None:
        if self.tenant_status.value == TenantStatusValue.DELETED:
            raise TenantDomainError("A deleted tenant cannot be updated.")
        if name is not None:
            self.tenant_name = name
        if slug is not None:
            self.tenant_slug = slug
        if settings is not None:
            self.settings = settings
        if metadata is not None:
            self.metadata = metadata
        if domains is not None:
            self.domains = domains
        self.updated_at = datetime.now(UTC)
        self._events.append(TenantUpdated.for_tenant(self.tenant_id))

    def activate(self) -> None:
        self.tenant_status = self.tenant_status.transition_to(TenantStatusValue.ACTIVE)
        self._record(TenantActivated)

    def suspend(self) -> None:
        self.tenant_status = self.tenant_status.transition_to(TenantStatusValue.SUSPENDED)
        self._record(TenantSuspended)

    def deactivate(self) -> None:
        self.tenant_status = self.tenant_status.transition_to(TenantStatusValue.INACTIVE)
        self._record(TenantDeactivated)

    def delete(self) -> None:
        if self.tenant_status.value == TenantStatusValue.DELETED:
            return
        self.tenant_status = TenantStatus(TenantStatusValue.DELETED)
        self._record(TenantDeleted)

    def pull_events(self) -> tuple[TenantDomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _record(self, event_type: type[TenantDomainEvent]) -> None:
        self.updated_at = datetime.now(UTC)
        self._events.append(event_type.for_tenant(self.tenant_id))
