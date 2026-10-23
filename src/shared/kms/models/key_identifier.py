"""KMS key purpose and resolved-key metadata."""

from __future__ import annotations

from enum import StrEnum


class KeyPurpose(StrEnum):
    """Cryptographic purpose used to validate a KMS key's usage."""

    ENCRYPTION = "encryption"
    DATA_KEY = "data_key"
    SIGNING = "signing"
