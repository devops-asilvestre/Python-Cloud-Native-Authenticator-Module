"""Base exception raised by the shared secrets foundation."""

from __future__ import annotations


class SecretException(Exception):
    """Base exception for all shared secrets failures."""

    def __init__(self, message: str, *, secret_name: str | None = None) -> None:
        super().__init__(message)
        self.secret_name = secret_name
