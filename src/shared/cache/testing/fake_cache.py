"""Compatibility facade for in-memory cache testing."""

from __future__ import annotations

from shared.cache.testing.fixtures import FakeRedisClient


class FakeCache:
    """Lightweight cache stub that mimics cache provider interactions."""

    def __init__(self) -> None:
        self.client = FakeRedisClient()

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> bool:
        return await self.client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> bool:
        return bool(await self.client.delete(key))

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def flush(self) -> bool:
        return await self.client.flushdb()
