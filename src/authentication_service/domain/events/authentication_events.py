from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class AuthenticationDomainEvent:
    tenant_id: str
    occurred_at: datetime
    event_id: UUID
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return type(self).__name__

    @classmethod
    def create(cls, tenant_id: str, user_id: str | None = None) -> AuthenticationDomainEvent:
        return cls(tenant_id, datetime.now(UTC), uuid4(), user_id)


@dataclass(frozen=True, slots=True)
class AuthenticationSucceeded(AuthenticationDomainEvent):
    session_id: str = ""


@dataclass(frozen=True, slots=True)
class AuthenticationFailed(AuthenticationDomainEvent):
    reason: str = "invalid_credentials"

    @classmethod
    def create(
        cls, tenant_id: str, user_id: str | None = None, reason: str = "invalid_credentials"
    ) -> AuthenticationFailed:
        return cls(tenant_id, datetime.now(UTC), uuid4(), user_id, reason)


@dataclass(frozen=True, slots=True)
class SessionCreated(AuthenticationDomainEvent):
    session_id: str = ""


@dataclass(frozen=True, slots=True)
class SessionTerminated(AuthenticationDomainEvent):
    session_id: str = ""


@dataclass(frozen=True, slots=True)
class PasswordChanged(AuthenticationDomainEvent):
    credential_id: str = ""


def event_payload(event: AuthenticationDomainEvent) -> dict[str, object]:
    """Return an explicit, non-sensitive event payload."""

    payload: dict[str, object] = {
        "event_id": str(event.event_id),
        "tenant_id": event.tenant_id,
        "occurred_at": event.occurred_at.isoformat(),
    }
    if event.user_id is not None:
        payload["user_id"] = event.user_id
    if isinstance(event, (AuthenticationSucceeded, SessionCreated, SessionTerminated)):
        payload["session_id"] = event.session_id
    if isinstance(event, AuthenticationFailed):
        payload["reason"] = event.reason
    if isinstance(event, PasswordChanged):
        payload["credential_id"] = event.credential_id
    return payload
