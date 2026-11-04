"""Redis connection factory with pydantic-backed configuration."""

from __future__ import annotations

from typing import Any, cast

from redis.asyncio import Redis

from shared.cache.exceptions.connection_exception import CacheConnectionException
from shared.cache.settings.redis_settings import RedisSettings


class RedisConnectionFactory:
    """Create configured Redis clients for async cache access."""

    def __init__(self, settings: RedisSettings | None = None) -> None:
        self._settings = settings or RedisSettings()

    @property
    def settings(self) -> RedisSettings:
        return self._settings

    def create(self) -> Redis:
        try:
            return Redis(**cast(dict[str, Any], self._settings.connection_kwargs))
        except Exception as exc:  # pragma: no cover - defensive guard
            raise CacheConnectionException("Unable to create Redis connection.") from exc

    def build_url(self) -> str:
        return self._settings.url


ConnectionFactory = RedisConnectionFactory
