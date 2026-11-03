import asyncio

import pytest

from tenant_service.application.commands import CreateTenant, UpdateTenant
from tenant_service.application.dto.tenant_dto import TenantCreateRequest, TenantUpdateRequest
from tenant_service.application.handlers.tenant_handlers import TenantHandlers
from tenant_service.application.queries import GetTenant
from tenant_service.domain.exceptions import TenantAlreadyExists
from tenant_service.domain.value_objects import TenantId
from tenant_service.infrastructure.events.in_memory_publisher import InMemoryEventPublisher
from tenant_service.infrastructure.persistence.in_memory_repository import InMemoryTenantRepository
from tenant_service.presentation.api.runtime import InMemoryTenantCache


def test_create_is_idempotent() -> None:
    asyncio.run(_assert_idempotent())


async def _assert_idempotent() -> None:
    handlers = TenantHandlers(
        InMemoryTenantRepository(), InMemoryTenantCache(), InMemoryEventPublisher()
    )
    request = TenantCreateRequest(name="Acme", code="ACME", slug="acme")
    first = await handlers.create(CreateTenant(request, "request-1"))
    second = await handlers.create(CreateTenant(request, "request-1"))
    assert first.tenant_id == second.tenant_id
    fetched = await handlers.get(GetTenant(TenantId(first.tenant_id)))
    assert fetched.tenant_id == first.tenant_id


def test_update_rejects_duplicate_slug() -> None:
    asyncio.run(_assert_duplicate_slug())


async def _assert_duplicate_slug() -> None:
    handlers = TenantHandlers(
        InMemoryTenantRepository(), InMemoryTenantCache(), InMemoryEventPublisher()
    )
    first = await handlers.create(
        CreateTenant(TenantCreateRequest(name="First Tenant", code="FIRST", slug="first"))
    )
    second = await handlers.create(
        CreateTenant(TenantCreateRequest(name="Second Tenant", code="SECOND", slug="second"))
    )
    with pytest.raises(TenantAlreadyExists):
        await handlers.update(
            UpdateTenant(TenantId(first.tenant_id), TenantUpdateRequest(slug=second.slug))
        )
