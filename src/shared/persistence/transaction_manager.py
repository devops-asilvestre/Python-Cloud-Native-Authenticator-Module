"""Context-managed transaction helper."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable

from contextlib import asynccontextmanager

from shared.persistence.unit_of_work import UnitOfWork


class TransactionManager:
    """Creates and manages transactional boundaries for a given unit-of-work."""

    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._unit_of_work: UnitOfWork | None = None

    async def __aenter__(self) -> UnitOfWork:
        self._unit_of_work = self._unit_of_work_factory()
        await self._unit_of_work.__aenter__()
        return self._unit_of_work

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        if self._unit_of_work is not None:
            await self._unit_of_work.__aexit__(exc_type, exc, tb)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[UnitOfWork]:
        async with self._unit_of_work_factory() as unit_of_work:
            yield unit_of_work
