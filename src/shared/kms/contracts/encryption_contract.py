"""Encryption service contract."""

from __future__ import annotations

from typing import Protocol

from shared.kms.models.encrypted_payload import EncryptedPayload


class EncryptionContract(Protocol):
    """Encrypt bytes through the shared KMS foundation."""

    def encrypt(
        self,
        plaintext: bytes,
        *,
        context: dict[str, str] | None = None,
    ) -> EncryptedPayload: ...
