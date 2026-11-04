"""Redis-based distributed lock implementation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from redis.asyncio import Redis

from shared.cache.contracts.lock_contract import DistributedLockContract
from shared.cache.exceptions.redis_exception import RedisException


class RedisDistributedLock(DistributedLockContract):
    """Simple distributed lock using Redis SET NX with expiry."""

    def __init__(
        self,
        redis_client: Redis,
        lock_name: str,
        *,
        owner: str | None = None,
        ttl_seconds: int = 30,
    ) -> None:
        self._redis_client = redis_client
        self._lock_name = lock_name
        self._owner = owner or "lock-owner"
        self._ttl_seconds = ttl_seconds
        self._acquired = False

    @property
    def lock_name(self) -> str:
        return self._lock_name

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def acquired(self) -> bool:
        return self._acquired

    async def acquire(self, *, timeout_seconds: float | None = None) -> bool:
        del timeout_seconds
        token = f"{self._owner}:{id(self)}"
        acquired = await self._redis_client.set(
            self._lock_name,
            token,
            nx=True,
            ex=self._ttl_seconds,
        )
        if acquired:
            self._acquired = True
        return bool(acquired)

    async def release(self) -> bool:
        if not self._acquired:
            return False
        token = await self._redis_client.get(self._lock_name)
        if token is None:
            self._acquired = False
            return False
        stored_token = token.decode("utf-8") if isinstance(token, bytes) else str(token)
        expected_token = f"{self._owner}:{id(self)}"
        if stored_token != expected_token:
            self._acquired = False
            return False
        deleted = await self._redis_client.delete(self._lock_name)
        self._acquired = False
        return bool(deleted)

    async def __aenter__(self) -> RedisDistributedLock:
        acquired = await self.acquire()
        if not acquired:
            raise RedisException("Unable to acquire Redis distributed lock.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> bool:
        await self.release()
        return False

    async def with_lock(
        self,
        callback: Callable[[], Awaitable[Any]],
        *,
        timeout_seconds: float | None = None,
    ) -> Any:
        acquired = await self.acquire(timeout_seconds=timeout_seconds)
        if not acquired:
            raise RedisException("Unable to acquire Redis distributed lock.")
        try:
            return await callback()
        finally:
            await self.release()
