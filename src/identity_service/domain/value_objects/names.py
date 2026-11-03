from __future__ import annotations

from dataclasses import dataclass

from identity_service.domain.exceptions import IdentityDomainError


def _validate(value: str, minimum: int, maximum: int, field: str) -> str:
    normalized = value.strip()
    if not minimum <= len(normalized) <= maximum:
        raise IdentityDomainError(f"{field} must have between {minimum} and {maximum} characters.")
    return normalized


@dataclass(frozen=True, slots=True)
class DisplayName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate(self.value, 3, 200, "DisplayName"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class GivenName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate(self.value, 2, 100, "GivenName"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FamilyName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _validate(self.value, 2, 150, "FamilyName"))

    def __str__(self) -> str:
        return self.value
