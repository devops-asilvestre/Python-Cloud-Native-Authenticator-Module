"""Factory for SQLAlchemy async engines."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from shared.persistence.connection_factory import ConnectionFactory
from shared.persistence.database_settings import DatabaseSettings


class EngineFactory:
    """Creates a database engine bound to the configured connection URI."""

    def __init__(
        self,
        connection_factory: ConnectionFactory | None = None,
        settings: DatabaseSettings | None = None,
    ) -> None:
        self._connection_factory = connection_factory or ConnectionFactory(settings)
        self._settings = settings or self._connection_factory.settings

    @property
    def connection_factory(self) -> ConnectionFactory:
        return self._connection_factory

    @property
    def settings(self) -> DatabaseSettings:
        return self._settings

    def create(self, **kwargs: Any) -> AsyncEngine:
        engine_kwargs: dict[str, Any] = {
            "echo": self._settings.echo,
            "pool_size": self._settings.pool_size,
            "max_overflow": self._settings.max_overflow,
            "pool_timeout": self._settings.pool_timeout,
            "pool_recycle": self._settings.pool_recycle,
        }
        engine_kwargs.update(kwargs)
        return create_async_engine(str(self._connection_factory), **engine_kwargs)
