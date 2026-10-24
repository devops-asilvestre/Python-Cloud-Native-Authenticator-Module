"""In-memory KMS provider for isolated tests."""

from __future__ import annotations

from typing import Any


class FakeKmsProvider:
    """Minimal deterministic provider implementing the production KMS contract."""

    def __init__(
        self,
        *,
        key_id: str = "test-key",
        key_arn: str = "arn:aws:kms:us-east-1:123456789012:key/test-key",
        key_usage: str = "ENCRYPT_DECRYPT",
        key_state: str = "Enabled",
        error: Exception | None = None,
    ) -> None:
        self.key_id = key_id
        self.key_arn = key_arn
        self.key_usage = key_usage
        self.key_state = key_state
        self.error = error
        self.calls: list[str] = []

    def _record(self, operation: str) -> None:
        self.calls.append(operation)
        if self.error is not None:
            raise self.error

    def describe_key(self, *, key_id: str) -> dict[str, Any]:
        self._record("describe_key")
        return {
            "KeyMetadata": {
                "KeyId": self.key_id,
                "Arn": self.key_arn,
                "KeyUsage": self.key_usage,
                "KeyState": self.key_state,
            }
        }

    def encrypt(
        self,
        *,
        key_id: str,
        plaintext: bytes,
        encryption_context: dict[str, str],
    ) -> dict[str, Any]:
        self._record("encrypt")
        return {"CiphertextBlob": b"fake-ciphertext"}

    def decrypt(
        self,
        *,
        ciphertext: bytes,
        encryption_context: dict[str, str],
    ) -> dict[str, Any]:
        self._record("decrypt")
        return {"Plaintext": b"fake-plaintext"}

    def generate_data_key(
        self,
        *,
        key_id: str,
        key_spec: str,
        encryption_context: dict[str, str],
    ) -> dict[str, Any]:
        self._record("generate_data_key")
        return {"Plaintext": b"fake-data-key", "CiphertextBlob": b"fake-encrypted-data-key"}

    def sign(
        self,
        *,
        key_id: str,
        message: bytes,
        signing_algorithm: str,
    ) -> dict[str, Any]:
        self._record("sign")
        return {"Signature": b"fake-signature"}

    def verify(
        self,
        *,
        key_id: str,
        message: bytes,
        signature: bytes,
        signing_algorithm: str,
    ) -> dict[str, Any]:
        self._record("verify")
        return {"SignatureValid": signature == b"fake-signature"}
