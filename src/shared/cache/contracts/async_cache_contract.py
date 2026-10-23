"""Async cache contract for Redis-backed implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AsyncCacheContract(ABC):
    """Asynchronous cache contract used by application services."""

    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> bool: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def flush(self) -> bool: ...
