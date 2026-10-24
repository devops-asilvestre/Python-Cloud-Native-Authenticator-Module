"""Histogram metric contract."""

from collections.abc import Mapping
from typing import Protocol


class HistogramContract(Protocol):
    """Contract for distribution or latency metrics."""

    name: str
    help_text: str
    unit: str

    def observe(self, value: float, *, labels: Mapping[str, str] | None = None) -> None: ...
