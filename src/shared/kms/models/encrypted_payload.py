"""Encrypted payload value model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EncryptedPayload:
    """Ciphertext and the metadata needed to decrypt it safely."""

    ciphertext: bytes
    key_id: str
    encryption_context: dict[str, str]
