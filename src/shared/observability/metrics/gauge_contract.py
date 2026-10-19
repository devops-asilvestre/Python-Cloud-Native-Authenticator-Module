"""Gauge metric contract."""

from collections.abc import Mapping
from typing import Protocol


class GaugeContract(Protocol):
    """Contract for values that can be observed as current state."""

    name: str
    help_text: str
    unit: str

    def set(self, value: float, *, labels: Mapping[str, str] | None = None) -> None: ...
