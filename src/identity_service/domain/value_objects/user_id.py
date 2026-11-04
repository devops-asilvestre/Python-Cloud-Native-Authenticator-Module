from __future__ import annotations

import uuid
from dataclasses import dataclass

from identity_service.domain.exceptions import IdentityDomainError
from shared.observability.correlation.uuidv7 import UUIDv7


@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        try:
            parsed = uuid.UUID(self.value)
        except (AttributeError, TypeError, ValueError) as exc:
            raise IdentityDomainError("UserId must be a valid UUIDv7.") from exc
        if parsed.version != 7:
            raise IdentityDomainError("UserId must be a UUIDv7.")
        object.__setattr__(self, "value", str(parsed))

    @classmethod
    def generate(cls) -> UserId:
        return cls(str(UUIDv7.generate()))

    def __str__(self) -> str:
        return self.value
