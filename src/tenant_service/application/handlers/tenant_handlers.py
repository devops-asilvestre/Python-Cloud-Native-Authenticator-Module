from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import Protocol

from shared.observability.logging.structured_logger import StructuredLogger
from tenant_service.application.commands import (
    ActivateTenant,
    CreateTenant,
    DeactivateTenant,
    DeleteTenant,
    SuspendTenant,
    UpdateTenant,
)
from tenant_service.application.dto.tenant_dto import TenantResponse
from tenant_service.application.queries import GetTenant, ListTenants
from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.events import TenantDomainEvent
from tenant_service.domain.exceptions import (
    IdempotencyConflict,
    TenantAlreadyExists,
    TenantNotFound,
)
from tenant_service.domain.repositories import TenantRepository
from tenant_service.domain.value_objects import (
    TenantCode,
    TenantDomain,
    TenantId,
    TenantMetadata,
    TenantName,
    TenantSettings,
    TenantSlug,
)


class TenantEventPublisher(Protocol):
    async def publish(self, event: TenantDomainEvent, tenant: Tenant) -> None: ...


class TenantCache(Protocol):
    async def get(self, tenant_id: TenantId) -> TenantResponse | None: ...
    async def set(self, tenant: Tenant) -> None: ...
    async def invalidate(self, tenant_id: TenantId) -> None: ...


class TenantHandlers:
    def __init__(
        self,
        repository: TenantRepository,
        cache: TenantCache,
        publisher: TenantEventPublisher,
        logger: StructuredLogger | None = None,
        idempotency: MutableMapping[str, tuple[TenantId, str]] | None = None,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.publisher = publisher
        self.logger = logger or StructuredLogger("tenant-service")
        self.idempotency = idempotency if idempotency is not None else {}

    async def create(self, command: CreateTenant) -> TenantResponse:
        request = command.request
        fingerprint = request.model_dump_json()
        if command.idempotency_key and command.idempotency_key in self.idempotency:
            existing_id, previous_fingerprint = self.idempotency[command.idempotency_key]
            if previous_fingerprint != fingerprint:
                raise IdempotencyConflict("Idempotency-Key was reused with a different request.")
            existing = await self.repository.get_by_id(existing_id)
            if existing is not None:
                return TenantResponse.from_domain(existing)
        code, slug = TenantCode(request.code), TenantSlug(request.slug)
        if await self.repository.exists(code, slug):
            raise TenantAlreadyExists("Tenant code or slug already exists.")
        tenant = Tenant.create(
            TenantName(request.name),
            code,
            slug,
            TenantSettings(**request.model_dump(include=set(TenantSettings.__dataclass_fields__))),
            TenantMetadata(request.metadata),
            tuple(TenantDomain(domain) for domain in request.domains),
        )
        await self.repository.save(tenant)
        if command.idempotency_key:
            self.idempotency[command.idempotency_key] = (tenant.tenant_id, fingerprint)
        await self._publish(tenant)
        self.logger.info("tenant_created", tenant_id=str(tenant.tenant_id))
        return TenantResponse.from_domain(tenant)

    async def get(self, query: GetTenant) -> TenantResponse:
        cached = await self.cache.get(query.tenant_id)
        if cached is not None:
            return cached
        tenant = await self._require(query.tenant_id)
        response = TenantResponse.from_domain(tenant)
        await self.cache.set(tenant)
        self.logger.info("tenant_read", tenant_id=str(tenant.tenant_id))
        return response

    async def list(self, query: ListTenants) -> Sequence[TenantResponse]:
        _ = query
        return [TenantResponse.from_domain(tenant) for tenant in await self.repository.list()]

    async def update(self, command: UpdateTenant) -> TenantResponse:
        tenant = await self._require(command.tenant_id)
        request = command.request
        if request.slug is not None:
            candidate_slug = TenantSlug(request.slug)
            existing = await self.repository.get_by_slug(candidate_slug)
            if existing is not None and existing.tenant_id != tenant.tenant_id:
                raise TenantAlreadyExists("Tenant slug already exists.")
        settings = TenantSettings(**request.settings.model_dump()) if request.settings else None
        tenant.update(
            name=TenantName(request.name) if request.name else None,
            slug=TenantSlug(request.slug) if request.slug else None,
            settings=settings,
            metadata=TenantMetadata(request.metadata) if request.metadata is not None else None,
            domains=tuple(TenantDomain(domain) for domain in request.domains)
            if request.domains is not None
            else None,
        )
        await self.repository.save(tenant)
        await self.cache.invalidate(command.tenant_id)
        await self._publish(tenant)
        self.logger.info("tenant_updated", tenant_id=str(tenant.tenant_id))
        return TenantResponse.from_domain(tenant)

    async def transition(self, tenant_id: TenantId, action: str) -> TenantResponse:
        tenant = await self._require(tenant_id)
        getattr(tenant, action)()
        await self.repository.save(tenant)
        await self.cache.invalidate(tenant_id)
        await self._publish(tenant)
        self.logger.info("tenant_transitioned", tenant_id=str(tenant_id), action=action)
        return TenantResponse.from_domain(tenant)

    async def activate(self, command: ActivateTenant) -> TenantResponse:
        return await self.transition(command.tenant_id, "activate")

    async def suspend(self, command: SuspendTenant) -> TenantResponse:
        return await self.transition(command.tenant_id, "suspend")

    async def deactivate(self, command: DeactivateTenant) -> TenantResponse:
        return await self.transition(command.tenant_id, "deactivate")

    async def delete(self, command: DeleteTenant) -> None:
        tenant = await self._require(command.tenant_id)
        tenant.delete()
        await self.repository.save(tenant)
        await self.cache.invalidate(command.tenant_id)
        await self._publish(tenant)
        self.logger.info("tenant_deleted", tenant_id=str(tenant.tenant_id))

    async def _require(self, tenant_id: TenantId) -> Tenant:
        tenant = await self.repository.get_by_id(tenant_id)
        if tenant is None:
            raise TenantNotFound(f"Tenant {tenant_id} was not found.")
        return tenant

    async def _publish(self, tenant: Tenant) -> None:
        for event in tenant.pull_events():
            await self.publisher.publish(event, tenant)
