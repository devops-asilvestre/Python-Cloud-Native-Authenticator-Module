import re
from dataclasses import dataclass

from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantSlug:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().lower()
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) is None:
            raise TenantDomainError("TenantSlug must be lowercase and URL-safe.")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
