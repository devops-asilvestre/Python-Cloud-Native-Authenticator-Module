"""Test fixtures for Redis cache components."""

from __future__ import annotations


class FakeRedisClient:
    """In-memory Redis emulator for unit tests."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.closed = False

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool | None = None,
    ) -> bool:
        if nx and key in self.store:
            return False
        self.store[key] = value
        if ex is not None:
            self.store[f"__ttl__:{key}"] = str(ex)
        return True

    async def delete(self, key: str) -> int:
        if key in self.store:
            del self.store[key]
            self.store.pop(f"__ttl__:{key}", None)
            return 1
        return 0

    async def exists(self, key: str) -> int:
        return 1 if key in self.store else 0

    async def flushdb(self) -> bool:
        self.store.clear()
        return True

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self.closed = True

    async def incr(self, key: str) -> int:
        current = int(self.store.get(key, "0"))
        current += 1
        self.store[key] = str(current)
        return current

    async def expire(self, key: str, seconds: int) -> bool:
        self.store[f"__ttl__:{key}"] = str(seconds)
        return True
