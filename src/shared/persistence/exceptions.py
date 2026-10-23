"""Persistence-specific exceptions."""

from __future__ import annotations


class PersistenceException(RuntimeError):
    """Base exception for persistence failures."""


class DatabaseConnectionException(PersistenceException):
    """Raised when a database connection cannot be established."""
