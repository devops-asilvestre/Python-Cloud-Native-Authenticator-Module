"""Async session factory for SQLAlchemy."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.persistence.database_settings import DatabaseSettings
from shared.persistence.engine_factory import EngineFactory


class SessionFactory:
    """Creates async sessions from a configured SQLAlchemy engine."""

    def __init__(
        self,
        engine_factory: EngineFactory | None = None,
        settings: DatabaseSettings | None = None,
        *,
        expire_on_commit: bool = False,
        autoflush: bool = False,
    ) -> None:
        self._settings = settings or DatabaseSettings()
        self._engine_factory = engine_factory or EngineFactory(settings=self._settings)
        self._engine = self._engine_factory.create()
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
        )

    @property
    def engine_factory(self) -> EngineFactory:
        return self._engine_factory

    @property
    def settings(self) -> DatabaseSettings:
        return self._settings

    def create(self, tenant_id: str | None = None) -> AsyncSession:
        session = self._session_factory()
        tenant = tenant_id or self._settings.default_tenant_id
        if tenant is not None:
            session.info[self._settings.tenant_field_name] = tenant
        return session
