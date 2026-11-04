from __future__ import annotations

import uuid
from dataclasses import dataclass

from shared.observability.correlation.uuidv7 import UUIDv7
from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantId:
    value: str

    def __post_init__(self) -> None:
        try:
            parsed = uuid.UUID(self.value)
        except (ValueError, AttributeError, TypeError) as exc:
            raise TenantDomainError("TenantId must be a valid UUIDv7.") from exc
        if parsed.version != 7:
            raise TenantDomainError("TenantId must be a UUIDv7.")
        object.__setattr__(self, "value", str(parsed))

    @classmethod
    def generate(cls) -> TenantId:
        return cls(str(UUIDv7.generate()))

    def __str__(self) -> str:
        return self.value
