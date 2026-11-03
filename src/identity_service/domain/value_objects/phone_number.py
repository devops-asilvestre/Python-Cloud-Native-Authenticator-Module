from __future__ import annotations

import re
from dataclasses import dataclass

from identity_service.domain.exceptions import IdentityDomainError


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        if re.fullmatch(r"\+[1-9]\d{7,14}", self.value) is None:
            raise IdentityDomainError("PhoneNumber must use E.164 format.")

    def __str__(self) -> str:
        return self.value
