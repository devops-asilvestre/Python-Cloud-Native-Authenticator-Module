"""Redis client provider to centralize connection lifecycle."""

from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from shared.cache.connection.connection_factory import RedisConnectionFactory
from shared.cache.exceptions.connection_exception import CacheConnectionException
from shared.observability.logging.logger_contract import LoggerContract


class RedisClientProvider:
    """Owns a single async Redis client and exposes connection lifecycle hooks."""

    def __init__(
        self,
        connection_factory: RedisConnectionFactory | None = None,
        *,
        logger: LoggerContract | None = None,
    ) -> None:
        self._connection_factory = connection_factory or RedisConnectionFactory()
        self._logger = logger
        self._client: Redis | None = None

    @property
    def connection_factory(self) -> RedisConnectionFactory:
        return self._connection_factory

    @property
    def client(self) -> Redis | None:
        return self._client

    async def get_client(self) -> Redis:
        if self._client is None:
            try:
                self._client = self._connection_factory.create()
            except CacheConnectionException:
                raise
            except Exception as exc:  # pragma: no cover - defensive guard
                raise CacheConnectionException("Unable to initialize Redis client.") from exc
            if self._logger is not None:
                self._logger.info(
                    "redis.client_configured",
                    host=self._connection_factory.settings.host,
                )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def ping(self) -> bool:
        client = await self.get_client()
        try:
            result = await client.ping()
            return bool(result)
        except Exception as exc:  # pragma: no cover - infrastructure/transport failure path
            raise CacheConnectionException("Redis health-check failed.") from exc

    async def __aenter__(self) -> RedisClientProvider:
        await self.get_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        await self.close()
