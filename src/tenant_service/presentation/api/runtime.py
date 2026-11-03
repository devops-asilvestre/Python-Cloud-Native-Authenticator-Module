from __future__ import annotations

import os
from collections.abc import AsyncIterator

from pydantic import ValidationError

from shared.cache.provider.cache_provider import CacheProvider
from shared.eventbus.publishers.eventbridge_publisher import EventBridgePublisher
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings
from shared.persistence.database_settings import DatabaseSettings
from shared.persistence.session_factory import SessionFactory
from shared.persistence.unit_of_work import SqlAlchemyUnitOfWork
from tenant_service.application.dto import TenantResponse
from tenant_service.application.handlers.tenant_handlers import TenantHandlers
from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.value_objects import TenantId
from tenant_service.infrastructure.cache.tenant_cache import RedisTenantCache
from tenant_service.infrastructure.events.event_publisher import EventPublisher
from tenant_service.infrastructure.events.unavailable_publisher import UnavailableEventPublisher
from tenant_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyTenantRepository,
)


class InMemoryTenantCache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def get(self, tenant_id: TenantId) -> TenantResponse | None:
        value = self.values.get(str(tenant_id))
        return value if isinstance(value, TenantResponse) else None

    async def set(self, tenant: Tenant) -> None:
        self.values[str(tenant.tenant_id)] = TenantResponse.from_domain(tenant)

    async def invalidate(self, tenant_id: TenantId) -> None:
        self.values.pop(str(tenant_id), None)


_session_factory = SessionFactory(settings=DatabaseSettings())
_cache = RedisTenantCache(CacheProvider())
_idempotency: dict[str, tuple[TenantId, str]] = {}


def _event_publisher() -> EventPublisher | UnavailableEventPublisher:
    try:
        return EventPublisher(
            EventBridgePublisher(
                EventBridgeSettings(
                    account_id=os.getenv("AUTHENTICATOR_EVENTBRIDGE_ACCOUNT_ID", ""),
                    bus_name=os.getenv("AUTHENTICATOR_EVENTBRIDGE_BUS_NAME", ""),
                    endpoint_url=os.getenv("AUTHENTICATOR_EVENTBRIDGE_ENDPOINT_URL"),
                )
            )
        )
    except ValidationError:
        return UnavailableEventPublisher()


async def get_handlers() -> AsyncIterator[TenantHandlers]:
    async with SqlAlchemyUnitOfWork(_session_factory) as unit_of_work:
        yield TenantHandlers(
            SqlAlchemyTenantRepository(unit_of_work.session),
            _cache,
            _event_publisher(),
            idempotency=_idempotency,
        )
