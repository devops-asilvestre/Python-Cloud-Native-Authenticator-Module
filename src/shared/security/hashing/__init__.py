"""Password hashing interface; hashing algorithms are supplied by adapters."""

from typing import Protocol


class PasswordHasher(Protocol):
    """Hash and verify passwords using an implementation-selected safe algorithm."""

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, encoded_hash: str) -> bool: ...
