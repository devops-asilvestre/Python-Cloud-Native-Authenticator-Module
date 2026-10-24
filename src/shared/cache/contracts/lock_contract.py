"""Distributed lock protocol for shared caching services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class LockContract(ABC):
    """Generic lock abstraction used by cache infrastructure."""

    @abstractmethod
    async def acquire(self, *, timeout_seconds: float | None = None) -> bool: ...

    @abstractmethod
    async def release(self) -> bool: ...

    @abstractmethod
    async def __aenter__(self) -> LockContract: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> bool: ...


class DistributedLockContract(LockContract, ABC):
    """Lock contract specialized for distributed coordination."""

    @abstractmethod
    async def with_lock(
        self,
        callback: Callable[[], Awaitable[T]],
        *,
        timeout_seconds: float | None = None,
    ) -> T: ...
