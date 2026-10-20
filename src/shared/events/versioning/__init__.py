"""Explicit event schema version."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class EventVersion:
    """Positive major version and non-negative minor version."""

    major: int
    minor: int = 0

    def __post_init__(self) -> None:
        if self.major < 1:
            raise ValueError("Event major version must be at least 1.")
        if self.minor < 0:
            raise ValueError("Event minor version cannot be negative.")
