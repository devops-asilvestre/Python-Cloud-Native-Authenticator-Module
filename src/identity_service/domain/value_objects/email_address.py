from __future__ import annotations

import re
from dataclasses import dataclass

from identity_service.domain.exceptions import IdentityDomainError

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().lower()
        if not _EMAIL.fullmatch(value):
            raise IdentityDomainError("EmailAddress must be a valid email address.")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
