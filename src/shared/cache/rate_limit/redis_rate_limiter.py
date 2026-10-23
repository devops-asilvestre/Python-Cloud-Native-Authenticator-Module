"""Redis-backed rate limiter implementation."""

from __future__ import annotations

from redis.asyncio import Redis

from shared.cache.contracts.rate_limit_contract import RateLimitContract


class RedisRateLimiter(RateLimitContract):
    """Fixed-window rate limiter backed by Redis counters."""

    def __init__(self, redis_client: Redis, *, window_seconds: int = 60) -> None:
        self._redis_client = redis_client
        self._window_seconds = window_seconds

    @property
    def redis_client(self) -> Redis:
        return self._redis_client

    async def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        current_window = window_seconds or self._window_seconds
        current = int(await self._redis_client.incr(key))
        if current == 1:
            await self._redis_client.expire(key, current_window)
        return current <= limit

    async def remaining(self, key: str, *, limit: int, window_seconds: int = 60) -> int:
        current = int(await self._redis_client.get(key) or 0)
        return max(0, limit - current)

    async def reset(self, key: str) -> bool:
        return bool(await self._redis_client.delete(key))
