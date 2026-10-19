"""Structured logger interface without a logging backend dependency."""

from collections.abc import Mapping
from typing import Protocol


class StructuredLogger(Protocol):
    """Minimal structured logging contract for adapters."""

    def debug(self, message: str, *, attributes: Mapping[str, object] | None = None) -> None: ...

    def info(self, message: str, *, attributes: Mapping[str, object] | None = None) -> None: ...

    def warning(self, message: str, *, attributes: Mapping[str, object] | None = None) -> None: ...

    def error(self, message: str, *, attributes: Mapping[str, object] | None = None) -> None: ...
