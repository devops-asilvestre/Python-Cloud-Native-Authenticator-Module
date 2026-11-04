"""Metric contract."""

from collections.abc import Mapping
from typing import Protocol


class MetricContract(Protocol):
    """Base contract for metric families."""

    name: str
    help_text: str
    unit: str

    def increment(self, value: float = 1.0, *, labels: Mapping[str, str] | None = None) -> None: ...

    def set(self, value: float, *, labels: Mapping[str, str] | None = None) -> None: ...

    def observe(self, value: float, *, labels: Mapping[str, str] | None = None) -> None: ...
