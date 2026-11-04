"""Compatibility wrapper for persistence exceptions."""

from shared.persistence.exceptions import DatabaseConnectionException, PersistenceException

__all__ = ["PersistenceException", "DatabaseConnectionException"]
