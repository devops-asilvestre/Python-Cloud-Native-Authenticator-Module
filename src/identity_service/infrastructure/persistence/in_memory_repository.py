from collections.abc import Sequence

from identity_service.domain.entities import User
from identity_service.domain.value_objects import EmailAddress, UserId, UserStatusValue, UserType


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], User] = {}

    async def save(self, user: User) -> None:
        self.values[(user.tenant_id, str(user.user_id))] = user

    async def get_by_id(self, tenant_id: str, user_id: UserId) -> User | None:
        return self.values.get((tenant_id, str(user_id)))

    async def get_by_email(self, tenant_id: str, email: EmailAddress) -> User | None:
        return next(
            (
                user
                for (scope, _), user in self.values.items()
                if scope == tenant_id
                and str(user.email) == str(email)
                and str(user.status) != "DELETED"
            ),
            None,
        )

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
    ) -> Sequence[User]:
        users = [user for (scope, _), user in self.values.items() if scope == tenant_id]
        if email:
            users = [user for user in users if email.lower() in str(user.email)]
        if name:
            needle = name.casefold()
            users = [user for user in users if needle in str(user.display_name).casefold()]
        if status:
            users = [user for user in users if user.status.value is status]
        if user_type:
            users = [user for user in users if user.type is user_type]
        users = [user for user in users if user.status.value is not UserStatusValue.DELETED]
        return users[offset : offset + limit]
