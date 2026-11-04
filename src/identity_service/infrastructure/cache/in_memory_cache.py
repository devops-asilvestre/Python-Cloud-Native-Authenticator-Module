from identity_service.application.dto import UserResponse
from identity_service.domain.entities import User
from identity_service.domain.value_objects import UserId


class InMemoryUserCache:
    def __init__(self) -> None:
        self.values: dict[str, UserResponse] = {}

    async def get(self, tenant_id: str, user_id: UserId) -> UserResponse | None:
        return self.values.get(f"{tenant_id}:{user_id}")

    async def set(self, user: User) -> None:
        self.values[f"{user.tenant_id}:{user.user_id}"] = UserResponse.from_domain(user)

    async def invalidate(self, tenant_id: str, user_id: UserId) -> None:
        self.values.pop(f"{tenant_id}:{user_id}", None)
