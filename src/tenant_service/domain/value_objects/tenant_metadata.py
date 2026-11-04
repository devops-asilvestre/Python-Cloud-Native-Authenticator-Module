from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from tenant_service.domain.exceptions import TenantDomainError

type MetadataValue = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class TenantMetadata:
    values: Mapping[str, MetadataValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not key.strip() for key in self.values):
            raise TenantDomainError("TenantMetadata keys cannot be blank.")
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
