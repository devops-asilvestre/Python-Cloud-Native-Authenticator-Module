from __future__ import annotations

import os
from collections.abc import AsyncIterator

from fastapi import Request

from authentication_service.application.authentication_service import (
    AuthenticationApplicationService,
)
from authentication_service.infrastructure.cache.rate_limiter import (
    RedisAuthenticationRateLimiter,
)
from authentication_service.infrastructure.cache.session_cache import SessionCache
from authentication_service.infrastructure.events.eventbridge_publisher import (
    EventBridgeAuthenticationPublisher,
)
from authentication_service.infrastructure.integration.foundation_adapters import (
    IdentityDirectoryAdapter,
    TenantFoundationAdapter,
)
from authentication_service.infrastructure.observability.metrics import (
    OpenTelemetryAuthenticationMetrics,
)
from authentication_service.infrastructure.persistence.audit_repository import (
    SqlAlchemyAuthenticationAuditRepository,
)
from authentication_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyCredentialRepository,
    SqlAlchemySessionRepository,
)
from identity_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyUserRepository,
)
from shared.cache.provider.cache_provider import RedisCacheProvider
from shared.eventbus.publishers.eventbridge_publisher import EventBridgePublisher
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings
from shared.events.metadata.event_context import EventContext
from shared.observability.logging.structured_logger import StructuredLogger
from shared.persistence.session_factory import SessionFactory
from tenant_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyTenantRepository,
)

_session_factory = SessionFactory()
_cache = RedisCacheProvider()

async def get_authentication_service(
    request: Request,
) -> AsyncIterator[AuthenticationApplicationService]:
    async with _session_factory.create(
        getattr(request.state.tenant_context, "tenant_id", None)
    ) as session:
        account_id = os.getenv("AUTHENTICATOR_EVENTBRIDGE_ACCOUNT_ID")
        bus_name = os.getenv("AUTHENTICATOR_EVENTBRIDGE_BUS_NAME")
        if not account_id or not bus_name:
            raise RuntimeError(
                "EventBridge configuration is required: account ID and bus name."
            )
        settings = EventBridgeSettings(
            account_id=account_id,
            bus_name=bus_name,
            endpoint_url=os.getenv("AUTHENTICATOR_EVENTBRIDGE_ENDPOINT_URL"),
        )
        publisher = EventBridgeAuthenticationPublisher(
            EventBridgePublisher(settings),
            lambda tenant: EventContext(tenant_id=tenant),
        )
        yield AuthenticationApplicationService(
            SqlAlchemyCredentialRepository(session),
            SqlAlchemySessionRepository(session),
            tenant_validator=TenantFoundationAdapter(SqlAlchemyTenantRepository(session)),
            identity_directory=IdentityDirectoryAdapter(SqlAlchemyUserRepository(session)),
            audit_sink=SqlAlchemyAuthenticationAuditRepository(session),
            session_cache=SessionCache(_cache),
            rate_limiter=RedisAuthenticationRateLimiter(_cache.client_provider),
            metrics=OpenTelemetryAuthenticationMetrics(),
            logger=StructuredLogger("authentication-service"),
            publisher=publisher,
        )
        await session.commit()


def session_factory() -> SessionFactory:
    return _session_factory
