from dataclasses import dataclass

from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantName:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()
        if not 3 <= len(value) <= 200:
            raise TenantDomainError("TenantName must contain 3 to 200 characters.")
        if any(ord(char) < 32 for char in value):
            raise TenantDomainError("TenantName cannot contain control characters.")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
