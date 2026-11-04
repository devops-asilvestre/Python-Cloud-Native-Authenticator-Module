from collections.abc import Sequence

from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.repositories import TenantRepository
from tenant_service.domain.value_objects import TenantCode, TenantId, TenantSlug


class InMemoryTenantRepository(TenantRepository):
    def __init__(self) -> None:
        self._items: dict[str, Tenant] = {}

    async def save(self, tenant: Tenant) -> None:
        self._items[str(tenant.tenant_id)] = tenant

    async def get_by_id(self, tenant_id: TenantId) -> Tenant | None:
        return self._items.get(str(tenant_id))

    async def get_by_code(self, code: TenantCode) -> Tenant | None:
        return next((item for item in self._items.values() if item.tenant_code == code), None)

    async def get_by_slug(self, slug: TenantSlug) -> Tenant | None:
        return next((item for item in self._items.values() if item.tenant_slug == slug), None)

    async def exists(self, code: TenantCode, slug: TenantSlug) -> bool:
        return await self.get_by_code(code) is not None or await self.get_by_slug(slug) is not None

    async def delete(self, tenant_id: TenantId) -> None:
        self._items.pop(str(tenant_id), None)

    async def list(self) -> Sequence[Tenant]:
        return tuple(self._items.values())
