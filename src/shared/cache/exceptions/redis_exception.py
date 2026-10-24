"""Base cache exception for Redis-backed operations."""

from __future__ import annotations


class RedisException(RuntimeError):
    """Raised when a Redis cache or lock operation fails."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code
