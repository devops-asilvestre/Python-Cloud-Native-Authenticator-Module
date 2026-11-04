import re
from dataclasses import dataclass

from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantCode:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().upper()
        if re.fullmatch(r"[A-Z0-9]{3,20}", value) is None:
            raise TenantDomainError("TenantCode must be 3 to 20 alphanumeric characters.")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
