"""Abstract tracing provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from shared.observability.tracing.trace_contract import TraceContract


class TracingProvider(ABC):
    """Abstract factory for trace implementations."""

    @abstractmethod
    def create_trace(self, *, trace_id: str | None = None) -> TraceContract: ...
