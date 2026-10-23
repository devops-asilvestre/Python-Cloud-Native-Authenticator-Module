"""Logger contract."""

from __future__ import annotations

from typing import Any, Protocol


class LoggerContract(Protocol):
    """Contract for structured logging providers."""

    def log(self, event: str, *, level: str = "INFO", **fields: Any) -> None: ...

    def debug(self, event: str, **fields: Any) -> None: ...

    def info(self, event: str, **fields: Any) -> None: ...

    def warning(self, event: str, **fields: Any) -> None: ...

    def error(self, event: str, **fields: Any) -> None: ...
