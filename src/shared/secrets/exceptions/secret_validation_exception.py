"""Raised when a secret name or payload violates company policy."""

from __future__ import annotations

from shared.secrets.exceptions.secret_exception import SecretException


class SecretValidationException(SecretException):
    """Raised when a secret name, payload, or value is invalid."""
