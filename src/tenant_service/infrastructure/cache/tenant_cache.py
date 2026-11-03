from __future__ import annotations

from typing import Protocol

from shared.cache.provider.cache_provider import CacheProvider
from tenant_service.application.dto import TenantResponse
from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.value_objects import TenantId


class TenantCacheProvider(Protocol):
    async def get(self, key: str) -> object | None: ...
    async def set(self, key: str, value: object, *, ttl_seconds: int | None = None) -> bool: ...
    async def delete(self, key: str) -> bool: ...


class RedisTenantCache:
    def __init__(self, provider: TenantCacheProvider | None = None, ttl_seconds: int = 300) -> None:
        self.provider = provider or CacheProvider()
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def key(tenant_id: TenantId) -> str:
        return f"tenant:{tenant_id}:aggregate"

    async def get(self, tenant_id: TenantId) -> TenantResponse | None:
        value = await self.provider.get(self.key(tenant_id))
        return TenantResponse.model_validate(value) if isinstance(value, dict) else None

    async def set(self, tenant: Tenant) -> None:
        await self.provider.set(
            self.key(tenant.tenant_id),
            TenantResponse.from_domain(tenant).model_dump(mode="json"),
            ttl_seconds=self.ttl_seconds,
        )

    async def invalidate(self, tenant_id: TenantId) -> None:
        await self.provider.delete(self.key(tenant_id))
