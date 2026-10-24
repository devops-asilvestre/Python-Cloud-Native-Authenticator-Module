"""Envelope-encryption data key result."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeneratedDataKey:
    """Plaintext key for immediate use and its KMS-encrypted form.

    Callers must use the plaintext key in memory and discard it after use.
    """

    plaintext_key: bytes
    ciphertext_key: bytes
    key_id: str
