import re
from dataclasses import dataclass

from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantDomain:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().lower()
        if re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", value) is None:
            raise TenantDomainError(
                "TenantDomain must be a valid hostname without protocol or path."
            )
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
