from __future__ import annotations

import uuid
from dataclasses import dataclass

from authentication_service.domain.exceptions import AuthenticationDomainError
from shared.observability.correlation.uuidv7 import UUIDv7


@dataclass(frozen=True, slots=True)
class SessionId:
    value: str

    def __post_init__(self) -> None:
        try:
            parsed = uuid.UUID(self.value)
        except (AttributeError, TypeError, ValueError) as exc:
            raise AuthenticationDomainError("SessionId must be a UUIDv7.") from exc
        if parsed.version != 7:
            raise AuthenticationDomainError("SessionId must be a UUIDv7.")
        object.__setattr__(self, "value", str(parsed))

    @classmethod
    def generate(cls) -> SessionId:
        return cls(str(UUIDv7.generate()))

    def __str__(self) -> str:
        return self.value

    def value_as_uuid(self) -> uuid.UUID:
        return uuid.UUID(self.value)
