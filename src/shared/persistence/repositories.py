"""Repository abstractions for domain data access."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class Repository[T](ABC):
    """Synchronous repository contract for shared persistence."""

    @abstractmethod
    def add(self, entity: T) -> None: ...

    @abstractmethod
    def get_by_id(self, entity_id: object) -> T | None: ...

    @abstractmethod
    def list(self) -> Sequence[T]: ...

    @abstractmethod
    def update(self, entity: T) -> None: ...

    @abstractmethod
    def delete(self, entity: T) -> None: ...


class AsyncRepository[T](ABC):
    """Asynchronous repository contract shared across bounded contexts."""

    @abstractmethod
    async def add(self, entity: T) -> None: ...

    @abstractmethod
    async def get_by_id(self, entity_id: object) -> T | None: ...

    @abstractmethod
    async def list(self) -> Sequence[T]: ...

    @abstractmethod
    async def update(self, entity: T) -> None: ...

    @abstractmethod
    async def delete(self, entity: T) -> None: ...
