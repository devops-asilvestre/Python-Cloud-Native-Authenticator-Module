from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from authentication_service.application.ports import TenantValidator
from authentication_service.infrastructure.integration.foundation_adapters import (
    TenantFoundationAdapter,
)
from shared.persistence.session_factory import SessionFactory
from tenant_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyTenantRepository,
)


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: str


class TenantContextResolver(Protocol):
    async def resolve(self, request: Request) -> TenantContext: ...


class HeaderTenantContextResolver:
    """Resolve and validate tenant scope through the configured foundation adapter."""

    def __init__(self, validator: TenantValidator) -> None:
        self._validator = validator

    async def resolve(self, request: Request) -> TenantContext:
        tenant_id = request.headers.get("X-Tenant-Id", "").strip()
        if not tenant_id:
            raise PermissionError("Tenant context is required.")
        await self._validator.ensure_active(tenant_id)
        return TenantContext(tenant_id)


class DatabaseTenantContextResolver:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    async def resolve(self, request: Request) -> TenantContext:
        tenant_id = request.headers.get("X-Tenant-Id", "").strip()
        if not tenant_id:
            raise PermissionError("Tenant context is required.")
        async with self._session_factory.create(tenant_id) as session:
            await TenantFoundationAdapter(
                SqlAlchemyTenantRepository(session)
            ).ensure_active(tenant_id)
        return TenantContext(tenant_id)


class TenantContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, resolver: TenantContextResolver) -> None:
        super().__init__(app)
        self._resolver = resolver

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not (
            request.url.path.startswith("/users")
            or request.url.path.startswith("/authentication")
        ):
            return await call_next(request)
        try:
            request.state.tenant_context = await self._resolver.resolve(request)
        except (PermissionError, ValueError):
            return Response("A valid active tenant context is required.", status_code=403)
        return await call_next(request)
