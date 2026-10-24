"""Raised when the secret provider cannot be accessed."""

from __future__ import annotations

from shared.secrets.exceptions.secret_exception import SecretException


class SecretAccessException(SecretException):
    """Raised when the underlying provider rejects the request."""
