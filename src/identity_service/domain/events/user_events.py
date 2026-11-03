from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from identity_service.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class UserDomainEvent:
    user_id: UserId
    tenant_id: str
    occurred_at: datetime
    event_id: UUID

    @property
    def event_type(self) -> str:
        return type(self).__name__

    @classmethod
    def for_user(cls, user_id: UserId, tenant_id: str) -> UserDomainEvent:
        return cls(user_id, tenant_id, datetime.now(UTC), uuid4())


@dataclass(frozen=True, slots=True)
class UserCreated(UserDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UserUpdated(UserDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UserActivated(UserDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UserSuspended(UserDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UserDeactivated(UserDomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UserDeleted(UserDomainEvent):
    pass
