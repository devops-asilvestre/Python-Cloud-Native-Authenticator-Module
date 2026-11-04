"""Factories for cache provider test doubles."""

from __future__ import annotations

from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.provider.cache_provider import CacheProvider
from shared.cache.testing.fixtures import FakeRedisClient


def make_client_provider() -> RedisClientProvider:
    client = FakeRedisClient()

    class _Provider(RedisClientProvider):
        def __init__(self) -> None:
            super().__init__()
            self._client = client  # type: ignore[assignment]

    return _Provider()


def make_cache_provider() -> CacheProvider:
    return CacheProvider(client_provider=make_client_provider())
