"""Tracing interface suitable for OpenTelemetry-backed adapters."""

from contextlib import AbstractContextManager
from typing import Protocol


class Span(Protocol):
    """Minimal span contract with explicit attribute and error recording."""

    def set_attribute(self, key: str, value: str | int | float | bool) -> None: ...

    def record_exception(self, exception: Exception) -> None: ...


class Tracer(Protocol):
    """Creates scoped spans without binding the shared kernel to a provider."""

    def start_span(self, name: str) -> AbstractContextManager[Span]: ...
