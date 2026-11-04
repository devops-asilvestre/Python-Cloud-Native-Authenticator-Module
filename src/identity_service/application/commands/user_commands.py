from __future__ import annotations

from dataclasses import dataclass

from identity_service.application.dto import UserCreateRequest, UserUpdateRequest
from identity_service.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class CreateUser:
    tenant_id: str
    request: UserCreateRequest
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateUser:
    tenant_id: str
    user_id: UserId
    request: UserUpdateRequest


@dataclass(frozen=True, slots=True)
class UserAction:
    tenant_id: str
    user_id: UserId
