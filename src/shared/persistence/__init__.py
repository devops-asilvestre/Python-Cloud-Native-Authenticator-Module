"""Shared persistence contracts and SQLAlchemy infrastructure."""

from shared.persistence.async_session_manager import AsyncSessionManager
from shared.persistence.connection_factory import ConnectionFactory
from shared.persistence.database_settings import DatabaseSettings
from shared.persistence.engine_factory import EngineFactory
from shared.persistence.exceptions import DatabaseConnectionException, PersistenceException
from shared.persistence.migration import MigrationFoundation
from shared.persistence.repositories import AsyncRepository, Repository
from shared.persistence.session_factory import SessionFactory
from shared.persistence.tenant import TenantContext
from shared.persistence.transaction_manager import TransactionManager
from shared.persistence.unit_of_work import SqlAlchemyUnitOfWork, UnitOfWork

__all__ = [
    "AsyncRepository",
    "AsyncSessionManager",
    "ConnectionFactory",
    "DatabaseConnectionException",
    "DatabaseSettings",
    "EngineFactory",
    "MigrationFoundation",
    "PersistenceException",
    "Repository",
    "SessionFactory",
    "SqlAlchemyUnitOfWork",
    "TenantContext",
    "TransactionManager",
    "UnitOfWork",
]
