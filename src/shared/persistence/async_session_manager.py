"""Lifecycle manager for a session during an async request."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from shared.persistence.exceptions import PersistenceException
from shared.persistence.session_factory import SessionFactory


class AsyncSessionManager:
    """Ensures a single async session is opened and closed for a unit of work."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise PersistenceException("No active async session is available.")
        return self._session

    async def __aenter__(self) -> AsyncSession:
        self._session = self._session_factory.create()
        return self._session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()

    def __call__(self) -> Awaitable[AsyncSession]:
        return self.__aenter__()
