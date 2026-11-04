from __future__ import annotations

from dataclasses import dataclass

from identity_service.domain.value_objects import UserId, UserStatusValue, UserType


@dataclass(frozen=True, slots=True)
class GetUser:
    tenant_id: str
    user_id: UserId


@dataclass(frozen=True, slots=True)
class SearchUsers:
    tenant_id: str
    email: str | None = None
    name: str | None = None
    status: UserStatusValue | None = None
    user_type: UserType | None = None
    offset: int = 0
    limit: int = 50
