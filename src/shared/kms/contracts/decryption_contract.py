"""Decryption service contract."""

from __future__ import annotations

from typing import Protocol


class DecryptionContract(Protocol):
    """Decrypt bytes through the shared KMS foundation."""

    def decrypt(
        self,
        ciphertext: bytes,
        *,
        context: dict[str, str] | None = None,
    ) -> bytes: ...
