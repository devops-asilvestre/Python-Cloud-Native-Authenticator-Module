"""Base fixture value used by shared-kernel tests."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FixtureBase[T]:
    """Named container for a value prepared for a test."""

    value: T
