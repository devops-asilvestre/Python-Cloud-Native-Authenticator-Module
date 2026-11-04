from __future__ import annotations

from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_HASHER = PasswordHasher()


@dataclass(frozen=True, slots=True)
class PasswordHash:
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("$argon2id$"):
            raise ValueError("PasswordHash must contain an Argon2id hash.")

    @classmethod
    def from_password(cls, password: str) -> PasswordHash:
        return cls(_HASHER.hash(password))

    def verify(self, password: str) -> bool:
        try:
            return _HASHER.verify(self.value, password)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False

    def needs_rehash(self) -> bool:
        return _HASHER.check_needs_rehash(self.value)
