"""Example usage for the shared Redis cache foundation."""

from __future__ import annotations

from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.provider.cache_provider import RedisCacheProvider


async def main() -> None:
    provider = RedisClientProvider()
    cache = RedisCacheProvider(client_provider=provider)

    await cache.set("example:key", {"tenant_id": "tenant-42", "status": "ready"}, ttl_seconds=60)
    value = await cache.get("example:key")
    assert value is not None

    await cache.delete("example:key")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
