import asyncio
from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from tenant_service.domain.value_objects import TenantCode, TenantId, TenantSlug
from tenant_service.infrastructure.persistence.models import TenantModel
from tenant_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyTenantRepository,
)
from tests.unit.tenant_service.test_domain import make_tenant


class ScalarRows:
    def __init__(self, rows: list[TenantModel]) -> None:
        self.rows = rows

    def __iter__(self) -> Iterator[TenantModel]:
        return iter(self.rows)


class FakeSession:
    def __init__(self) -> None:
        self.models: dict[str, TenantModel] = {}
        self.added: list[TenantModel] = []
        self.deleted: list[TenantModel] = []
        self.scalar_result: object | None = None
        self.scalars_result = ScalarRows([])
        self.get = AsyncMock(side_effect=self._get)
        self.scalar = AsyncMock(side_effect=self._scalar)
        self.scalars = AsyncMock(side_effect=self._scalars)
        self.flush = AsyncMock()
        self.delete = AsyncMock(side_effect=self._delete)

    async def _get(self, model_type: type[TenantModel], key: str) -> TenantModel | None:
        _ = model_type
        return self.models.get(key)

    async def _scalar(self, statement: object) -> object | None:
        _ = statement
        return self.scalar_result

    async def _scalars(self, statement: object) -> ScalarRows:
        _ = statement
        return self.scalars_result

    async def _delete(self, model: TenantModel) -> None:
        self.deleted.append(model)

    def add(self, model: TenantModel) -> None:
        self.added.append(model)
        self.models[model.tenant_id] = model


def test_sqlalchemy_repository_round_trip_and_queries() -> None:
    asyncio.run(_assert_repository_round_trip())


async def _assert_repository_round_trip() -> None:
    session = FakeSession()
    repository = SqlAlchemyTenantRepository(session)  # type: ignore[arg-type]
    tenant = make_tenant()

    await repository.save(tenant)
    assert len(session.added) == 1
    model = session.added[0]
    assert model.tenant_code == "ACME"
    assert (await repository.get_by_id(tenant.tenant_id)) is not None

    await repository.save(tenant)
    assert len(session.added) == 1
    session.scalar_result = model
    assert (await repository.get_by_code(TenantCode("ACME"))) is not None
    assert (await repository.get_by_slug(TenantSlug("acme"))) is not None
    assert await repository.exists(TenantCode("ACME"), TenantSlug("other"))

    session.scalars_result = ScalarRows([model])
    assert len(await repository.list()) == 1
    await repository.delete(tenant.tenant_id)
    assert session.deleted == [model]


def test_sqlalchemy_repository_handles_missing_records_and_maps_models() -> None:
    asyncio.run(_assert_missing_and_mapping())


async def _assert_missing_and_mapping() -> None:
    session = FakeSession()
    repository = SqlAlchemyTenantRepository(session)  # type: ignore[arg-type]
    tenant = make_tenant()
    model = TenantModel(
        tenant_id=str(tenant.tenant_id),
        tenant_name=str(tenant.tenant_name),
        tenant_code=str(tenant.tenant_code),
        tenant_slug=str(tenant.tenant_slug),
        tenant_status=str(tenant.tenant_status),
        settings={
            "timezone": "UTC",
            "language": "en",
            "country": "US",
            "currency": "USD",
            "branding_enabled": False,
            "audit_enabled": True,
            "mfa_required": False,
        },
        metadata_={"plan": "standard"},
        domains=["acme.com"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.models[model.tenant_id] = model
    session.scalar_result = None
    assert await repository.get_by_code(TenantCode("ACME")) is None
    assert await repository.get_by_slug(TenantSlug("acme")) is None
    assert not await repository.exists(TenantCode("ACME"), TenantSlug("acme"))
    await repository.delete(TenantId.generate())
    assert session.deleted == []
