from fastapi.testclient import TestClient

from identity_service.main import app
from tenant_service.application.handlers.tenant_handlers import TenantHandlers
from tenant_service.domain.value_objects import TenantId
from tenant_service.infrastructure.events.in_memory_publisher import InMemoryEventPublisher
from tenant_service.infrastructure.persistence.in_memory_repository import InMemoryTenantRepository
from tenant_service.presentation.api.runtime import InMemoryTenantCache, get_handlers

_idempotency: dict[str, tuple[TenantId, str]] = {}
_repository = InMemoryTenantRepository()
_cache = InMemoryTenantCache()
_publisher = InMemoryEventPublisher()


def test_tenant_api_crud_and_lifecycle() -> None:
    app.dependency_overrides[get_handlers] = lambda: TenantHandlers(
        _repository,
        _cache,
        _publisher,
        idempotency=_idempotency,
    )
    client = TestClient(app)
    payload = {"name": "Acme API", "code": "API01", "slug": "acme-api"}
    created = client.post("/tenants", json=payload, headers={"Idempotency-Key": "api-1"})
    assert created.status_code == 201
    tenant = created.json()
    tenant_id = tenant["tenant_id"]
    repeated = client.post("/tenants", json=payload, headers={"Idempotency-Key": "api-1"})
    assert repeated.status_code == 201
    assert repeated.json()["tenant_id"] == tenant_id
    assert client.post(f"/tenants/{tenant_id}/activate").status_code == 200
    assert client.get(f"/tenants/{tenant_id}").json()["status"] == "ACTIVE"
    assert client.put(f"/tenants/{tenant_id}", json={"name": "Acme Updated"}).status_code == 200
    assert client.delete(f"/tenants/{tenant_id}").status_code == 204
    assert (
        client.post(
            "/tenants",
            json={
                "name": "Bad",
                "code": "BAD",
                "slug": "bad",
                "domains": ["https://bad"],
            },
        ).status_code
        == 422
    )
    app.dependency_overrides.clear()
