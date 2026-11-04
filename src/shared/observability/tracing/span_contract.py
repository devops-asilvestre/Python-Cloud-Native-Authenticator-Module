"""Span contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class SpanContract(Protocol):
    """Contract representing an active unit of work in a distributed trace."""

    name: str
    trace_id: str
    span_id: str

    def set_attribute(self, key: str, value: Any) -> None: ...

    def add_event(self, event: str, *, attributes: Mapping[str, Any] | None = None) -> None: ...

    def finish(self) -> None: ...
