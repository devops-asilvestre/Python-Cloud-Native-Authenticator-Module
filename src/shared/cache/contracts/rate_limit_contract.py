"""Rate limiting contract for shared cache layer."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RateLimitContract(ABC):
    """Interface for token-bucket or fixed-window rate limiting."""

    @abstractmethod
    async def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool: ...

    @abstractmethod
    async def remaining(self, key: str, *, limit: int, window_seconds: int = 60) -> int: ...

    @abstractmethod
    async def reset(self, key: str) -> bool: ...
