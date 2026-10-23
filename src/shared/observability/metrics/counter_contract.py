"""Counter metric contract."""

from collections.abc import Mapping
from typing import Protocol


class CounterContract(Protocol):
    """Contract for monotonically increasing metrics."""

    name: str
    help_text: str
    unit: str

    def increment(self, value: float = 1.0, *, labels: Mapping[str, str] | None = None) -> None: ...
