from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from authentication_service.domain.events import (
    AuthenticationDomainEvent,
    SessionCreated,
    SessionTerminated,
)
from authentication_service.domain.exceptions import InvalidCredentialState
from authentication_service.domain.value_objects import SessionId, SessionMetadata


@dataclass(slots=True)
class AuthenticationSession:
    session_id: SessionId
    tenant_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    metadata: SessionMetadata
    active: bool = True
    _events: list[AuthenticationDomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls, tenant_id: str, user_id: str, *, ttl: timedelta = timedelta(hours=8),
        metadata: SessionMetadata | None = None, now: datetime | None = None,
    ) -> AuthenticationSession:
        if not tenant_id.strip() or not user_id.strip() or ttl <= timedelta(0):
            raise InvalidCredentialState("A valid tenant, user and session TTL are required.")
        created = (now or datetime.now(UTC)).astimezone(UTC)
        session_id = SessionId.generate()
        session = cls(
            session_id, tenant_id, user_id, created, created + ttl, metadata or SessionMetadata()
        )
        session._events.append(
            SessionCreated(tenant_id, created, uuid4(), user_id, str(session_id))
        )
        return session

    @classmethod
    def restore(
        cls, *, session_id: str, tenant_id: str, user_id: str, created_at: datetime,
        expires_at: datetime, active: bool,
    ) -> AuthenticationSession:
        return cls(
            SessionId(session_id), tenant_id, user_id, created_at, expires_at,
            SessionMetadata(), active,
        )

    def terminate(self) -> None:
        if self.active:
            self.active = False
            self._events.append(
                SessionTerminated(self.tenant_id, datetime.now(UTC), uuid4(), self.user_id,
                                  str(self.session_id))
            )

    def is_valid(self, now: datetime | None = None) -> bool:
        current = (now or datetime.now(UTC)).astimezone(UTC)
        return self.active and current < self.expires_at

    def pull_events(self) -> tuple[AuthenticationDomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events
