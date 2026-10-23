import asyncio
from types import SimpleNamespace

from sqlalchemy.ext.asyncio import AsyncEngine

from shared.persistence import (
    AsyncSessionManager,
    ConnectionFactory,
    DatabaseConnectionException,
    DatabaseSettings,
    EngineFactory,
    MigrationFoundation,
    PersistenceException,
    SessionFactory,
    SqlAlchemyUnitOfWork,
    TenantContext,
    TransactionManager,
)


class FakeAsyncSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1

    async def close(self) -> None:
        self.close_calls += 1


def test_database_settings_builds_expected_postgres_url() -> None:
    settings = DatabaseSettings(
        host="postgres.local",
        port=5433,
        username="tenant_admin",
        password="s3cr3t",
        database="authenticator",
    )

    assert settings.database_url == (
        "postgresql+asyncpg://tenant_admin:s3cr3t@postgres.local:5433/authenticator"
    )
    assert settings.async_database_url == settings.database_url


def test_connection_factory_and_engine_factory_create_configured_values() -> None:
    settings = DatabaseSettings(
        driver="postgresql+asyncpg",
        host="localhost",
        port=5432,
        username="authenticator",
        password="authenticator",
        database="authenticator",
        echo=True,
    )
    connection_factory = ConnectionFactory(settings)
    engine_factory = EngineFactory(connection_factory)

    assert connection_factory.build_url() == settings.database_url
    engine = engine_factory.create()

    assert isinstance(engine, AsyncEngine)
    assert str(engine.url).startswith("postgresql+asyncpg://")
    assert engine.echo is True


def test_session_factory_creates_async_session() -> None:
    settings = DatabaseSettings(username="app_user", password="secret", database="tenant_db")
    engine_factory = EngineFactory(ConnectionFactory(settings))
    session_factory = SessionFactory(engine_factory)

    session = session_factory.create(tenant_id="tenant-42")

    assert session is not None
    assert session.bind is not None
    assert str(session.bind.url).startswith("postgresql+asyncpg://")
    assert session.info["tenant_id"] == "tenant-42"


def test_tenant_context_maps_to_session_metadata() -> None:
    tenant = TenantContext(tenant_id="tenant-7", user_id="user-9", metadata={"region": "us-east-1"})

    assert tenant.as_session_info() == {
        "tenant_id": "tenant-7",
        "user_id": "user-9",
        "region": "us-east-1",
    }


def test_async_session_manager_manages_lifecycle() -> None:
    session = FakeAsyncSession()
    factory = SimpleNamespace(create=lambda: session)
    manager = AsyncSessionManager(factory)

    async def run() -> None:
        async with manager as active_session:
            assert active_session is session
            assert manager.session is session
        assert session.close_calls == 1

    asyncio.run(run())


def test_sqlalchemy_unit_of_work_commits_and_rolls_back() -> None:
    session = FakeAsyncSession()
    factory = SimpleNamespace(create=lambda: session)

    async def successful_work() -> None:
        async with SqlAlchemyUnitOfWork(factory) as unit_of_work:
            assert unit_of_work.session is session
        assert session.commit_calls == 1
        assert session.rollback_calls == 0

    async def failing_work() -> None:
        try:
            async with SqlAlchemyUnitOfWork(factory):
                raise ValueError("boom")
        except ValueError:
            pass
        assert session.rollback_calls == 1
        assert session.close_calls >= 1

    asyncio.run(successful_work())
    asyncio.run(failing_work())


def test_transaction_manager_wraps_unit_of_work() -> None:
    session = FakeAsyncSession()
    factory = SimpleNamespace(create=lambda: session)

    async def run() -> None:
        async with TransactionManager(lambda: SqlAlchemyUnitOfWork(factory)) as work:
            assert isinstance(work, SqlAlchemyUnitOfWork)
            assert work.session is session
        assert session.commit_calls == 1

    asyncio.run(run())


def test_migration_foundation_builds_alembic_config() -> None:
    settings = DatabaseSettings(host="db", username="ops", password="strong", database="platform")
    foundation = MigrationFoundation(settings=settings, directory="src/shared/persistence/alembic")

    config = foundation.build_config(version_locations="versions")

    assert config["script_location"] == "src/shared/persistence/alembic"
    assert config["sqlalchemy.url"] == settings.database_url
    assert config["version_locations"] == "versions"
    assert foundation.alembic_ini_path.name == "alembic.ini"


def test_persistence_exceptions_are_distinct_types() -> None:
    assert issubclass(PersistenceException, RuntimeError)
    assert issubclass(DatabaseConnectionException, PersistenceException)
