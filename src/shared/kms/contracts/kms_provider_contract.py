"""AWS KMS provider contract."""

from __future__ import annotations

from typing import Any, Protocol


class KmsProviderContract(Protocol):
    """Allowed KMS cryptographic and metadata operations."""

    def describe_key(self, *, key_id: str) -> dict[str, Any]: ...

    def encrypt(
        self, *, key_id: str, plaintext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]: ...

    def decrypt(
        self, *, ciphertext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]: ...

    def generate_data_key(
        self, *, key_id: str, key_spec: str, encryption_context: dict[str, str]
    ) -> dict[str, Any]: ...

    def sign(
        self, *, key_id: str, message: bytes, signing_algorithm: str
    ) -> dict[str, Any]: ...

    def verify(
        self,
        *,
        key_id: str,
        message: bytes,
        signature: bytes,
        signing_algorithm: str,
    ) -> dict[str, Any]: ...
