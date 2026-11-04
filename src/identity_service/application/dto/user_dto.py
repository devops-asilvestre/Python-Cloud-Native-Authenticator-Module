from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from identity_service.domain.entities import User
from identity_service.domain.value_objects import UserType


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str
    display_name: str = Field(min_length=3, max_length=200)
    given_name: str = Field(min_length=2, max_length=100)
    family_name: str = Field(min_length=2, max_length=150)
    phone_number: str
    type: UserType
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    display_name: str | None = Field(default=None, min_length=3, max_length=200)
    given_name: str | None = Field(default=None, min_length=2, max_length=100)
    family_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone_number: str | None = None
    metadata: dict[str, str | int | float | bool | None] | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    tenant_id: str
    email: str
    display_name: str
    given_name: str
    family_name: str
    phone_number: str
    status: str
    type: str
    metadata: dict[str, str | int | float | bool | None]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            user_id=str(user.user_id),
            tenant_id=user.tenant_id,
            email=str(user.email),
            display_name=str(user.display_name),
            given_name=str(user.given_name),
            family_name=str(user.family_name),
            phone_number=str(user.phone_number),
            status=str(user.status),
            type=str(user.type),
            metadata=dict(user.metadata.values),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
