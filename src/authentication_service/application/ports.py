from __future__ import annotations

from typing import Protocol

from authentication_service.domain.events import AuthenticationDomainEvent


class AuthenticationEventPublisher(Protocol):
    async def publish(self, event: AuthenticationDomainEvent) -> None: ...


class NullAuthenticationEventPublisher:
    async def publish(self, event: AuthenticationDomainEvent) -> None:
        return None


class TenantValidator(Protocol):
    async def ensure_active(self, tenant_id: str) -> None: ...


class IdentityDirectory(Protocol):
    async def ensure_active_user(self, tenant_id: str, user_id: str) -> None: ...


class AuthenticationAuditSink(Protocol):
    async def record(self, event: AuthenticationDomainEvent) -> None: ...


class AuthenticationLogger(Protocol):
    def info(self, event: str, **fields: object) -> None: ...
    def warning(self, event: str, **fields: object) -> None: ...


class AuthenticationMetrics(Protocol):
    def observe(self, name: str, value: float, **attributes: str) -> None: ...


class AuthenticationRateLimiter(Protocol):
    async def allow(self, tenant_id: str, email: str, ip_address: str | None) -> bool: ...


class NullTenantValidator:
    async def ensure_active(self, tenant_id: str) -> None:
        if not tenant_id.strip():
            raise ValueError("A tenant_id is required.")


class NullIdentityDirectory:
    async def ensure_active_user(self, tenant_id: str, user_id: str) -> None:
        if not tenant_id.strip() or not user_id.strip():
            raise ValueError("A tenant and user are required.")


class InMemoryAuthenticationAuditSink:
    def __init__(self) -> None:
        self.events: list[AuthenticationDomainEvent] = []

    async def record(self, event: AuthenticationDomainEvent) -> None:
        self.events.append(event)


class NullAuthenticationMetrics:
    def observe(self, name: str, value: float, **attributes: str) -> None:
        return None


class AllowAllAuthenticationRateLimiter:
    async def allow(self, tenant_id: str, email: str, ip_address: str | None) -> bool:
        return True
