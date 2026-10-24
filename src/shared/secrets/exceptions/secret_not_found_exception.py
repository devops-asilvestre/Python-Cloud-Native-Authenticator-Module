"""Raised when a secret does not exist or is unavailable."""

from __future__ import annotations

from shared.secrets.exceptions.secret_exception import SecretException


class SecretNotFoundException(SecretException):
    """Raised when the target secret cannot be resolved."""
