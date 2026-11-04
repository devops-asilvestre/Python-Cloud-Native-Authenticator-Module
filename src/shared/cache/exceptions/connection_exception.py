"""Connection errors raised by the shared cache adapter."""

from __future__ import annotations

from shared.cache.exceptions.redis_exception import RedisException


class CacheConnectionException(RedisException):
    """Raised when a Redis connection cannot be established or verified."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message, code=code or "CACHE_CONNECTION_ERROR")
