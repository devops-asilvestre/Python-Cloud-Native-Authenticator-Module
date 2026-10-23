"""Concrete async cache provider with Redis-backed storage and contracts."""

from __future__ import annotations

from typing import Any

from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.contracts.async_cache_contract import AsyncCacheContract
from shared.cache.contracts.session_cache_contract import SessionCacheContract
from shared.cache.contracts.token_cache_contract import TokenCacheContract
from shared.cache.keys.tenant_key_builder import TenantAwareKeyBuilder
from shared.cache.serialization.json_serializer import JsonSerializer


class CacheProvider(AsyncCacheContract):
    """Default async cache abstraction with JSON serialization and tenant context."""

    def __init__(
        self,
        client_provider: RedisClientProvider | None = None,
        *,
        key_builder: TenantAwareKeyBuilder | None = None,
        serializer: JsonSerializer | None = None,
    ) -> None:
        self._client_provider = client_provider or RedisClientProvider()
        self._key_builder = key_builder or TenantAwareKeyBuilder()
        self._serializer = serializer or JsonSerializer()

    @property
    def client_provider(self) -> RedisClientProvider:
        return self._client_provider

    @property
    def key_builder(self) -> TenantAwareKeyBuilder:
        return self._key_builder

    @property
    def serializer(self) -> JsonSerializer:
        return self._serializer

    async def get(self, key: str) -> Any | None:
        client = await self._client_provider.get_client()
        raw = await client.get(key)
        if raw is None:
            return None
        return self._serializer.loads(raw)

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> bool:
        client = await self._client_provider.get_client()
        payload = self._serializer.dumps(value)
        if ttl_seconds is None:
            result = await client.set(key, payload)
        else:
            result = await client.set(key, payload, ex=ttl_seconds)
        return bool(result)

    async def delete(self, key: str) -> bool:
        client = await self._client_provider.get_client()
        return bool(await client.delete(key))

    async def exists(self, key: str) -> bool:
        client = await self._client_provider.get_client()
        return bool(await client.exists(key))

    async def flush(self) -> bool:
        client = await self._client_provider.get_client()
        result = await client.flushdb()
        return bool(result)

    async def get_session(self, tenant_id: str, session_id: str) -> Any | None:
        return await self.get(self._key_builder.session_key(tenant_id, session_id))

    async def set_session(
        self,
        tenant_id: str,
        session_id: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        return await self.set(
            self._key_builder.session_key(tenant_id, session_id),
            value,
            ttl_seconds=ttl_seconds,
        )

    async def delete_session(self, tenant_id: str, session_id: str) -> bool:
        return await self.delete(self._key_builder.session_key(tenant_id, session_id))

    async def get_token(self, tenant_id: str, token_id: str) -> Any | None:
        return await self.get(self._key_builder.token_key(tenant_id, token_id))

    async def set_token(
        self,
        tenant_id: str,
        token_id: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        return await self.set(
            self._key_builder.token_key(tenant_id, token_id),
            value,
            ttl_seconds=ttl_seconds,
        )

    async def delete_token(self, tenant_id: str, token_id: str) -> bool:
        return await self.delete(self._key_builder.token_key(tenant_id, token_id))


class RedisCacheProvider(CacheProvider, SessionCacheContract, TokenCacheContract):
    """Concrete Redis provider that exposes session and token-specific contracts."""

    pass


RedisProvider = RedisCacheProvider
