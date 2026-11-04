"""Unit-of-work abstraction for SQLAlchemy-based persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from shared.persistence.exceptions import PersistenceException
from shared.persistence.session_factory import SessionFactory


class UnitOfWork(ABC):
    """Contract for explicit transactional boundaries."""

    @property
    @abstractmethod
    def session(self) -> AsyncSession: ...

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Concrete transactional unit that manages an async SQLAlchemy session."""

    def __init__(
        self,
        session_factory: SessionFactory | Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise PersistenceException("No active SQLAlchemy session available.")
        return self._session

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        if callable(self._session_factory):
            session_factory = self._session_factory
            self._session = (
                session_factory()
                if not isinstance(session_factory, SessionFactory)
                else session_factory.create()
            )
        else:
            self._session = self._session_factory.create()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self._session is not None:
                await self._session.close()
                self._session = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()
