"""Alembic environment for the shared persistence foundation."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from authentication_service.infrastructure.persistence.models import AuthenticationBase
from shared.persistence.database_settings import DatabaseSettings
from tenant_service.infrastructure.persistence.models import TenantBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = DatabaseSettings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# This migration scaffold intentionally keeps the shared layer technology-neutral.
# Concrete bounded contexts can attach their metadata if and when they have models.
target_metadata = TenantBase.metadata
for table in AuthenticationBase.metadata.tables.values():
    table.to_metadata(target_metadata)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
