"""Expected AWS KMS usage for cryptographic purposes."""

from __future__ import annotations

from dataclasses import dataclass

from shared.kms.models.key_identifier import KeyPurpose


@dataclass(frozen=True, slots=True)
class KeyUsageMetadata:
    """Map an application purpose to the AWS KMS key usage constraint."""

    purpose: KeyPurpose
    aws_key_usage: str

    @classmethod
    def for_purpose(cls, purpose: KeyPurpose) -> KeyUsageMetadata:
        usage = "SIGN_VERIFY" if purpose is KeyPurpose.SIGNING else "ENCRYPT_DECRYPT"
        return cls(purpose=purpose, aws_key_usage=usage)
