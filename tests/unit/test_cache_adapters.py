from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from shared.cache.connection.connection_factory import RedisConnectionFactory
from shared.cache.exceptions.redis_exception import RedisException
from shared.cache.locks.redis_distributed_lock import RedisDistributedLock
from shared.cache.rate_limit.redis_rate_limiter import RedisRateLimiter
from shared.cache.settings.redis_settings import RedisSettings


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.counts: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def set(self, key: str, value: str, *, nx: bool, ex: int) -> bool:
        if nx and key in self.values:
            return False
        self.values[key] = value
        self.expirations[key] = ex
        return True

    async def get(self, key: str) -> str | None:
        value = self.values.get(key)
        if value is not None:
            return value
        count = self.counts.get(key)
        return str(count) if count is not None else None

    async def delete(self, key: str) -> int:
        existed = self.values.pop(key, None) is not None
        existed = self.counts.pop(key, None) is not None or existed
        return int(existed)

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int) -> bool:
        self.expirations[key] = seconds
        return True


def test_redis_settings_build_secure_urls_and_kwargs() -> None:
    settings = RedisSettings(
        host="redis.example", port=6380, db=2, username="app", password="secret", ssl=True
    )
    assert settings.url == "rediss://app:secret@redis.example:6380/2"
    assert settings.dsn == settings.url
    assert settings.connection_kwargs["ssl"] is True
    assert settings.connection_kwargs["username"] == "app"


def test_redis_connection_factory_builds_client_configuration() -> None:
    factory = RedisConnectionFactory(RedisSettings(host="localhost", port=6379))
    assert factory.build_url() == "redis://localhost:6379/0"
    client = factory.create()
    asyncio.run(client.aclose())


def test_distributed_lock_acquire_release_context_and_callback() -> None:
    async def scenario() -> None:
        redis = FakeRedis()
        lock = RedisDistributedLock(redis, "lock", owner="owner", ttl_seconds=10)  # type: ignore[arg-type]
        assert await lock.acquire()
        assert lock.acquired
        assert not await RedisDistributedLock(redis, "lock").acquire()  # type: ignore[arg-type]
        assert await lock.release()
        assert not lock.acquired
        assert await lock.with_lock(_value)
        async with RedisDistributedLock(redis, "lock", owner="context") as active:
            assert active.acquired

    async def _value() -> str:
        return "done"

    asyncio.run(scenario())


def test_distributed_lock_rejects_foreign_and_unavailable_tokens() -> None:
    async def scenario() -> None:
        redis = FakeRedis()
        lock = RedisDistributedLock(redis, "lock", owner="owner")  # type: ignore[arg-type]
        assert not await lock.release()
        assert await lock.acquire()
        redis.values["lock"] = "foreign"
        assert not await lock.release()
        redis.values.pop("lock")
        assert not await lock.release()

    asyncio.run(scenario())


def test_rate_limiter_enforces_window_and_reset() -> None:
    async def scenario() -> None:
        redis = FakeRedis()
        limiter = RedisRateLimiter(redis, window_seconds=30)  # type: ignore[arg-type]
        assert await limiter.allow("key", limit=1)
        assert not await limiter.allow("key", limit=1, window_seconds=5)
        assert await limiter.remaining("key", limit=3) == 1
        assert await limiter.reset("key")

    asyncio.run(scenario())


def test_lock_callback_failure_releases_lock() -> None:
    async def scenario() -> None:
        redis = FakeRedis()
        lock = RedisDistributedLock(redis, "lock")  # type: ignore[arg-type]
        callback = AsyncMock(side_effect=RuntimeError("boom"))
        with pytest.raises(RuntimeError):
            await lock.with_lock(callback)
        assert not lock.acquired
        assert "lock" not in redis.values

    asyncio.run(scenario())


def test_lock_context_fails_when_already_owned() -> None:
    async def scenario() -> None:
        redis = FakeRedis()
        first = RedisDistributedLock(redis, "lock", owner="first")  # type: ignore[arg-type]
        second = RedisDistributedLock(redis, "lock", owner="second")  # type: ignore[arg-type]
        assert await first.acquire()
        with pytest.raises(RedisException):
            async with second:
                pass
        await first.release()

    asyncio.run(scenario())
