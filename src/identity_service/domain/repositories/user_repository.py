from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from identity_service.domain.entities import User
from identity_service.domain.value_objects import EmailAddress, UserId, UserStatusValue, UserType


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...
    async def get_by_id(self, tenant_id: str, user_id: UserId) -> User | None: ...
    async def get_by_email(self, tenant_id: str, email: EmailAddress) -> User | None: ...
    async def search(
        self,
        tenant_id: str,
        *,
        email: str | None = None,
        name: str | None = None,
        status: UserStatusValue | None = None,
        user_type: UserType | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[User]: ...
