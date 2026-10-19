"""Metrics interface suitable for OpenTelemetry-backed adapters."""

from collections.abc import Mapping
from typing import Protocol


class Counter(Protocol):
    """Monotonically increasing measurement."""

    def add(self, value: int, *, attributes: Mapping[str, str] | None = None) -> None: ...


class Histogram(Protocol):
    """Distribution measurement."""

    def record(self, value: float, *, attributes: Mapping[str, str] | None = None) -> None: ...
