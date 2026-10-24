"""Factory contract for creating test values."""

from typing import Protocol


class FactoryBase[T](Protocol):
    """Interface for factories that produce deterministic test values."""

    def build(self) -> T: ...
