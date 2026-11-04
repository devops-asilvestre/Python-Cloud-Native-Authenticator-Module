from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from tenant_service.domain.exceptions import InvalidTenantTransition, TenantDomainError


class TenantStatusValue(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"
    DELETED = "DELETED"


@dataclass(frozen=True, slots=True)
class TenantStatus:
    value: TenantStatusValue

    def __post_init__(self) -> None:
        if not isinstance(self.value, TenantStatusValue):
            try:
                object.__setattr__(self, "value", TenantStatusValue(str(self.value).upper()))
            except ValueError as exc:
                raise TenantDomainError("TenantStatus is invalid.") from exc

    @classmethod
    def pending(cls) -> TenantStatus:
        return cls(TenantStatusValue.PENDING)

    def transition_to(self, target: TenantStatusValue) -> TenantStatus:
        allowed = {
            TenantStatusValue.PENDING: {TenantStatusValue.ACTIVE},
            TenantStatusValue.ACTIVE: {TenantStatusValue.SUSPENDED, TenantStatusValue.INACTIVE},
            TenantStatusValue.SUSPENDED: {TenantStatusValue.ACTIVE},
            TenantStatusValue.INACTIVE: {TenantStatusValue.ACTIVE},
            TenantStatusValue.DELETED: set(),
        }
        if target not in allowed[self.value]:
            raise InvalidTenantTransition(f"{self.value} -> {target} is not allowed.")
        return TenantStatus(target)

    def __str__(self) -> str:
        return self.value.value
