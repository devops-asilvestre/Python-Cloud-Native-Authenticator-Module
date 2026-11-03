import asyncio

from tenant_service.domain.value_objects import TenantCode, TenantSlug
from tenant_service.infrastructure.persistence.in_memory_repository import InMemoryTenantRepository
from tests.unit.tenant_service.test_domain import make_tenant


def test_repository_preserves_unique_lookup_contracts() -> None:
    asyncio.run(_assert_repository_contract())


async def _assert_repository_contract() -> None:
    repository = InMemoryTenantRepository()
    tenant = make_tenant()
    await repository.save(tenant)
    assert await repository.get_by_id(tenant.tenant_id) is tenant
    assert await repository.get_by_code(TenantCode("ACME")) is tenant
    assert await repository.get_by_slug(TenantSlug("acme")) is tenant
    assert await repository.exists(TenantCode("ACME"), TenantSlug("other"))
    assert len(await repository.list()) == 1
    await repository.delete(tenant.tenant_id)
    assert await repository.get_by_id(tenant.tenant_id) is None
