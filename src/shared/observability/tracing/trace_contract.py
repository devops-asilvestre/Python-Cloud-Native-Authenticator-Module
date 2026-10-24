"""Trace contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from shared.observability.tracing.span_contract import SpanContract


class TraceContract(Protocol):
    """Contract for a tracing provider that orchestrates spans."""

    trace_id: str

    def start_span(
        self,
        name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ) -> SpanContract: ...

    def get_current_span(self) -> SpanContract | None: ...
