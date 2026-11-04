import asyncio
from typing import cast

from shared.eventbus.models.publish_result import PublishResult
from shared.events import EventEnvelope
from tenant_service.domain.value_objects import TenantId
from tenant_service.infrastructure.cache.tenant_cache import RedisTenantCache
from tenant_service.infrastructure.events.event_publisher import EventPublisher
from tenant_service.infrastructure.events.tenant_event_contracts import (
    TENANT_EVENT_VERSION,
    TenantEventPayload,
    build_tenant_event_registry,
)
from tests.unit.tenant_service.test_domain import make_tenant


class FakeProvider:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def get(self, key: str) -> object | None:
        return self.values.get(key)

    async def set(self, key: str, value: object, *, ttl_seconds: int | None = None) -> bool:
        self.values[key] = value
        return ttl_seconds == 300

    async def delete(self, key: str) -> bool:
        return self.values.pop(key, None) is not None


class FakePublisher:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> PublishResult:
        self.events.append(event)
        return PublishResult(
            message_id="message",
            bus_name="tenant",
            sequence_number="1",
            success=True,
        )


def test_redis_cache_adapter() -> None:
    asyncio.run(_assert_cache())


async def _assert_cache() -> None:
    provider = FakeProvider()
    cache = RedisTenantCache(provider)
    tenant = make_tenant()
    await cache.set(tenant)
    assert (await cache.get(TenantId(str(tenant.tenant_id)))) is not None
    await cache.invalidate(tenant.tenant_id)
    assert await cache.get(tenant.tenant_id) is None


def test_event_publisher_adapter_builds_versioned_envelope() -> None:
    asyncio.run(_assert_event_publisher())


async def _assert_event_publisher() -> None:
    publisher = FakePublisher()
    adapter = EventPublisher(publisher)
    tenant = make_tenant()
    event = tenant.pull_events()[0]
    await adapter.publish(event, tenant)
    assert cast(EventEnvelope, publisher.events[0]).event_type == "tenant.tenant.created"


def test_tenant_event_contracts_are_registered_and_closed() -> None:
    registry = build_tenant_event_registry()
    schema = registry.resolve("tenant.tenant.created", TENANT_EVENT_VERSION)
    assert schema is TenantEventPayload
