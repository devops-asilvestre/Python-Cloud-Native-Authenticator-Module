from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from identity_service.domain.exceptions import InvalidUserTransition


class UserStatusValue(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


@dataclass(frozen=True, slots=True)
class UserStatus:
    value: UserStatusValue

    @classmethod
    def pending(cls) -> UserStatus:
        return cls(UserStatusValue.PENDING)

    def transition_to(self, target: UserStatusValue) -> UserStatus:
        allowed = {
            UserStatusValue.PENDING: {UserStatusValue.ACTIVE},
            UserStatusValue.ACTIVE: {
                UserStatusValue.INACTIVE,
                UserStatusValue.SUSPENDED,
                UserStatusValue.DELETED,
            },
            UserStatusValue.INACTIVE: {UserStatusValue.ACTIVE, UserStatusValue.DELETED},
            UserStatusValue.SUSPENDED: {UserStatusValue.ACTIVE},
        }
        if target not in allowed.get(self.value, set()):
            raise InvalidUserTransition(f"Cannot transition user from {self.value} to {target}.")
        return UserStatus(target)

    def __str__(self) -> str:
        return self.value.value
