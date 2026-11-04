import asyncio

import pytest

from tenant_service.application.commands import CreateTenant, UpdateTenant
from tenant_service.application.dto.tenant_dto import TenantCreateRequest, TenantUpdateRequest
from tenant_service.application.handlers.tenant_handlers import TenantHandlers
from tenant_service.application.queries import GetTenant
from tenant_service.domain.exceptions import (
    IdempotencyConflict,
    TenantAlreadyExists,
    TenantDomainError,
    TenantNotFound,
)
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
    with pytest.raises(IdempotencyConflict):
        await handlers.create(
            CreateTenant(
                TenantCreateRequest(name="Different", code="DIFF", slug="different"),
                "request-1",
            )
        )
    assert (await handlers.get(GetTenant(TenantId(first.tenant_id)))).tenant_id == first.tenant_id


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


def test_handler_errors_and_all_lifecycle_commands() -> None:
    asyncio.run(_assert_handler_errors_and_lifecycle())


async def _assert_handler_errors_and_lifecycle() -> None:
    from tenant_service.application.commands import (
        ActivateTenant,
        DeactivateTenant,
        DeleteTenant,
        SuspendTenant,
    )

    handlers = TenantHandlers(
        InMemoryTenantRepository(), InMemoryTenantCache(), InMemoryEventPublisher()
    )
    missing = TenantId.generate()
    with pytest.raises(TenantNotFound):
        await handlers.get(GetTenant(missing))
    with pytest.raises(TenantNotFound):
        await handlers.activate(ActivateTenant(missing))
    with pytest.raises(TenantNotFound):
        await handlers.suspend(SuspendTenant(missing))
    with pytest.raises(TenantNotFound):
        await handlers.deactivate(DeactivateTenant(missing))
    with pytest.raises(TenantNotFound):
        await handlers.delete(DeleteTenant(missing))

    created = await handlers.create(
        CreateTenant(TenantCreateRequest(name="Lifecycle", code="LIFE", slug="lifecycle"))
    )
    tenant_id = TenantId(created.tenant_id)
    await handlers.activate(ActivateTenant(tenant_id))
    await handlers.suspend(SuspendTenant(tenant_id))
    await handlers.activate(ActivateTenant(tenant_id))
    await handlers.deactivate(DeactivateTenant(tenant_id))
    await handlers.delete(DeleteTenant(tenant_id))
    with pytest.raises(TenantDomainError):
        await handlers.update(
            UpdateTenant(tenant_id, TenantUpdateRequest(name="Deleted tenant"))
        )
