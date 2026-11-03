from __future__ import annotations

from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.keys.tenant_key_builder import TenantAwareKeyBuilder


class RedisAuthenticationRateLimiter:
    def __init__(
        self,
        client_provider: RedisClientProvider | None = None,
        *,
        key_builder: TenantAwareKeyBuilder | None = None,
        limit: int = 10,
        window_seconds: int = 60,
    ) -> None:
        self._provider = client_provider or RedisClientProvider()
        self._keys = key_builder or TenantAwareKeyBuilder()
        self._limit = limit
        self._window_seconds = window_seconds

    async def allow(self, tenant_id: str, email: str, ip_address: str | None) -> bool:
        client = await self._provider.get_client()
        identifiers = [f"user:{email.strip().lower()}"]
        if ip_address:
            identifiers.append(f"ip:{ip_address}")
        for identifier in identifiers:
            key = self._keys.rate_limit_key(tenant_id, identifier)
            count = int(await client.incr(key))
            if count == 1:
                await client.expire(key, self._window_seconds)
            if count > self._limit:
                return False
        return True
