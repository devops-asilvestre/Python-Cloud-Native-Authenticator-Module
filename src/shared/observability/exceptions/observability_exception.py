"""Observability-specific exceptions."""

from __future__ import annotations


class TelemetryException(RuntimeError):
    """Raised when telemetry components cannot satisfy their contract."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code is None:
            return self.message
        return f"[{self.code}] {self.message}"
