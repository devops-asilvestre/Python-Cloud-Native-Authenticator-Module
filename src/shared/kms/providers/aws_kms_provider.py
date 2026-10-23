"""AWS KMS provider restricted to approved read and crypto operations."""

from __future__ import annotations

from typing import Any

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.settings.kms_settings import KmsSettings


class AwsKmsProvider(KmsProviderContract):
    """Thin AWS KMS adapter; key lifecycle and policy APIs are intentionally absent."""

    def __init__(
        self,
        *,
        client_factory: AwsClientFactory | None = None,
        settings: KmsSettings | None = None,
    ) -> None:
        self.settings = settings or KmsSettings()
        self._client_factory = client_factory or AwsClientFactory()

    def _client(self) -> Any:
        return self._client_factory.create_client(
            "kms",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.endpoint_url,
        )

    @staticmethod
    def _response(response: Any) -> dict[str, Any]:
        if not isinstance(response, dict):
            raise TypeError("AWS KMS returned a non-dictionary response.")
        return response

    def describe_key(self, *, key_id: str) -> dict[str, Any]:
        return self._response(self._client().describe_key(KeyId=key_id))

    def encrypt(
        self, *, key_id: str, plaintext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        return self._response(
            self._client().encrypt(
                KeyId=key_id,
                Plaintext=plaintext,
                EncryptionContext=encryption_context,
            )
        )

    def decrypt(
        self, *, ciphertext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        return self._response(
            self._client().decrypt(
                CiphertextBlob=ciphertext,
                EncryptionContext=encryption_context,
            )
        )

    def generate_data_key(
        self, *, key_id: str, key_spec: str, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        return self._response(
            self._client().generate_data_key(
                KeyId=key_id,
                KeySpec=key_spec,
                EncryptionContext=encryption_context,
            )
        )

    def sign(
        self, *, key_id: str, message: bytes, signing_algorithm: str
    ) -> dict[str, Any]:
        return self._response(
            self._client().sign(
                KeyId=key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=signing_algorithm,
            )
        )

    def verify(
        self,
        *,
        key_id: str,
        message: bytes,
        signature: bytes,
        signing_algorithm: str,
    ) -> dict[str, Any]:
        return self._response(
            self._client().verify(
                KeyId=key_id,
                Message=message,
                MessageType="RAW",
                Signature=signature,
                SigningAlgorithm=signing_algorithm,
            )
        )
