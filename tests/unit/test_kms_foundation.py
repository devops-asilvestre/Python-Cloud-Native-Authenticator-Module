from __future__ import annotations

from typing import Any

import pytest
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.kms.context.crypto_context import build_encryption_context
from shared.kms.context.kms_context import KmsContext
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_decryption_exception import KmsDecryptionException
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.kms.exceptions.kms_signing_exception import KmsSigningException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.providers.aws_kms_provider import AwsKmsProvider
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.kms.resolver.kms_resolver import KmsResolver
from shared.kms.services.datakey_service import DataKeyService
from shared.kms.services.decryption_service import DecryptionService
from shared.kms.services.encryption_service import EncryptionService
from shared.kms.services.signing_service import SigningService
from shared.kms.services.verification_service import VerificationService
from shared.kms.settings.kms_settings import KmsSettings
from shared.kms.testing.factories import build_fake_kms_provider, build_kms_settings
from shared.kms.testing.fake_kms import FakeKmsProvider as SharedFakeKmsProvider
from shared.kms.testing.fixtures import kms_settings_fixture
from shared.kms.validation.kms_connection_validator import KmsConnectionValidator
from shared.kms.validation.kms_health_check import KmsHealthCheck
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger
from shared.secrets.resolver.secret_resolver import SecretResolver


class FakeBotoKmsClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def _call(self, operation: str, **kwargs: object) -> dict[str, object]:
        self.calls.append((operation, kwargs))
        return {"operation": operation}

    def describe_key(self, **kwargs: object) -> dict[str, object]:
        return self._call("describe_key", **kwargs)

    def encrypt(self, **kwargs: object) -> dict[str, object]:
        return self._call("encrypt", **kwargs)

    def decrypt(self, **kwargs: object) -> dict[str, object]:
        return self._call("decrypt", **kwargs)

    def generate_data_key(self, **kwargs: object) -> dict[str, object]:
        return self._call("generate_data_key", **kwargs)

    def sign(self, **kwargs: object) -> dict[str, object]:
        return self._call("sign", **kwargs)

    def verify(self, **kwargs: object) -> dict[str, object]:
        return self._call("verify", **kwargs)


class FakeAwsClientFactory(AwsClientFactory):
    def __init__(self, client: FakeBotoKmsClient) -> None:
        self.client = client
        self.options: dict[str, object] = {}

    def create_client(
        self,
        service_name: str,
        *,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        session: Any = None,
        config: Any = None,
    ) -> FakeBotoKmsClient:
        self.options = {
            "service_name": service_name,
            "region_name": region_name,
            "endpoint_url": endpoint_url,
        }
        return self.client


class FakeKmsProvider:
    def __init__(self) -> None:
        self.usage = "ENCRYPT_DECRYPT"
        self.key_state = "Enabled"
        self.raise_error = False
        self.raise_aws_error = False
        self.fail_describe = False
        self.context: dict[str, str] = {}
        self.describe_response: dict[str, Any] | None = None

    def describe_key(self, *, key_id: str) -> dict[str, Any]:
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.fail_describe:
            raise ClientError({"Error": {"Code": "NotFoundException"}}, "DescribeKey")
        if self.describe_response is not None:
            return self.describe_response
        usage = "SIGN_VERIFY" if key_id == "alias/test-signing" else self.usage
        return {
            "KeyMetadata": {
                "KeyId": "key-123",
                "Arn": "arn:aws:kms:us-east-1:123456789012:key/key-123",
                "KeyUsage": usage,
                "KeyState": self.key_state,
            }
        }

    def encrypt(
        self, *, key_id: str, plaintext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        self.context = encryption_context
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.raise_error:
            raise ClientError({"Error": {"Code": "InternalException"}}, "Encrypt")
        return {"CiphertextBlob": b"encrypted"}

    def decrypt(
        self, *, ciphertext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        self.context = encryption_context
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.raise_error:
            raise ClientError({"Error": {"Code": "InvalidCiphertextException"}}, "Decrypt")
        return {"Plaintext": b"plaintext"}

    def generate_data_key(
        self, *, key_id: str, key_spec: str, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.raise_error:
            raise ClientError({"Error": {"Code": "InternalException"}}, "GenerateDataKey")
        return {"Plaintext": b"data-key", "CiphertextBlob": b"encrypted-key"}

    def sign(self, *, key_id: str, message: bytes, signing_algorithm: str) -> dict[str, Any]:
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.raise_error:
            raise ClientError({"Error": {"Code": "InternalException"}}, "Sign")
        return {"Signature": b"signature"}

    def verify(
        self,
        *,
        key_id: str,
        message: bytes,
        signature: bytes,
        signing_algorithm: str,
    ) -> dict[str, Any]:
        if self.raise_aws_error:
            raise AwsAuthenticationException("credentials unavailable")
        if self.raise_error:
            raise ClientError({"Error": {"Code": "InternalException"}}, "Verify")
        return {"SignatureValid": signature == b"signature"}


@pytest.fixture
def kms() -> tuple[FakeKmsProvider, KmsKeyResolver]:
    provider = FakeKmsProvider()
    settings = KmsSettings(
        kms_key_alias="alias/test-key",
        kms_signing_key_alias="alias/test-signing",
        environment="test",
    )
    return provider, KmsKeyResolver(provider, settings)


def test_settings_require_region_and_key_identifier() -> None:
    with pytest.raises(KmsConfigurationException):
        KmsSettings(environment="test")
    with pytest.raises(KmsConfigurationException):
        KmsSettings(kms_key_id=" ", environment="test")
    with pytest.raises(KmsConfigurationException):
        KmsSettings(aws_region="not-a-region", kms_key_id="key-123", environment="test")
    assert KmsSettings(
        aws_region="eusc-de-east-1",
        kms_key_alias="alias/eusc",
        environment="test",
    ).aws_region == "eusc-de-east-1"
    with pytest.raises(KmsConfigurationException):
        KmsSettings(kms_key_alias=" ", environment="test")
    with pytest.raises(KmsConfigurationException):
        KmsSettings(kms_key_id="key-123", account_id="invalid", environment="test")
    with pytest.raises(KmsConfigurationException):
        KmsSettings(kms_key_alias="alias/test", environment=" ")
    assert KmsSettings(kms_key_alias="alias/test", environment="test").endpoint_url is None
    assert KmsSettings(
        kms_key_id="key-123",
        kms_key_alias="alias/test",
        environment="test",
    ).key_identifier == "key-123"
    assert KmsSettings(
        kms_key_alias="alias/encryption",
        kms_signing_key_id="signing-key",
        environment="test",
    ).key_identifier_for_signing() == "signing-key"


def test_settings_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTHENTICATOR_KMS_AWS_REGION", "eu-west-1")
    monkeypatch.setenv("AUTHENTICATOR_KMS_KEY_ID", "key-from-env")
    monkeypatch.setenv("AUTHENTICATOR_KMS_SIGNING_KEY_ALIAS", "alias/sign-from-env")
    monkeypatch.setenv("AUTHENTICATOR_ENVIRONMENT", "test")

    settings = KmsSettings()

    assert settings.aws_region == "eu-west-1"
    assert settings.key_identifier == "key-from-env"
    assert settings.key_identifier_for_signing() == "alias/sign-from-env"
    assert settings.environment == "test"


def test_settings_require_environment_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AUTHENTICATOR_ENVIRONMENT", raising=False)
    with pytest.raises(KmsConfigurationException):
        KmsSettings.model_validate({"kms_key_alias": "alias/test"})


def test_resolver_validates_purpose_and_enabled_state(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    assert resolver.resolve(None, KeyPurpose.ENCRYPTION).key_id == "key-123"
    assert resolver.resolve(None, KeyPurpose.SIGNING).key_usage == "SIGN_VERIFY"
    provider.key_state = "Disabled"
    with pytest.raises(KmsValidationException):
        resolver.resolve(None, KeyPurpose.SIGNING)


def test_context_binds_tenant_and_rejects_conflicts() -> None:
    assert build_encryption_context({"purpose": "token"}, tenant_id="tenant-a") == {
        "purpose": "token",
        "tenant_id": "tenant-a",
    }
    with pytest.raises(KmsValidationException):
        build_encryption_context({"tenant_id": "tenant-b"}, tenant_id="tenant-a")
    with pytest.raises(KmsValidationException):
        build_encryption_context({"": "value"}, tenant_id=None)
    with pytest.raises(KmsValidationException):
        build_encryption_context({"purpose": ""}, tenant_id=None)
    request_context = RequestContext(tenant_id="tenant-a")
    kms_context = KmsContext.from_request_context(request_context)
    assert kms_context.encryption_context({"purpose": "refresh-token"}) == {
        "tenant_id": "tenant-a",
        "purpose": "refresh-token",
    }


def test_encrypt_decrypt_validate_payload_and_bind_tenant(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    request = RequestContext(tenant_id="tenant-a")
    encryption = EncryptionService(provider, resolver, request_context=request)
    decryption = DecryptionService(provider, resolver, request_context=request)

    encrypted = encryption.encrypt(b"secret")
    assert encrypted.ciphertext == b"encrypted"
    assert provider.context["tenant_id"] == "tenant-a"
    assert decryption.decrypt(encrypted.ciphertext) == b"plaintext"
    with pytest.raises(KmsEncryptionException):
        encryption.encrypt(b"")
    with pytest.raises(KmsEncryptionException):
        encryption.encrypt(b"secret", context={"tenant_id": "tenant-b"})
    with pytest.raises(KmsDecryptionException):
        decryption.decrypt(b"")


def test_encryption_data_key_and_decryption_errors_are_wrapped(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    provider.raise_error = True
    with pytest.raises(KmsEncryptionException):
        EncryptionService(provider, resolver).encrypt(b"payload")
    with pytest.raises(KmsEncryptionException):
        DataKeyService(provider, resolver).generate()
    with pytest.raises(KmsDecryptionException):
        DecryptionService(provider, resolver).decrypt(b"ciphertext")
    provider.raise_error = False
    provider.fail_describe = True
    with pytest.raises(KmsEncryptionException):
        EncryptionService(provider, resolver).encrypt(b"payload")
    provider.fail_describe = False
    provider.raise_error = True
    provider.usage = "SIGN_VERIFY"
    with pytest.raises(KmsSigningException):
        SigningService(provider, resolver).sign(b"payload")

    provider.raise_error = False
    provider.raise_aws_error = True
    with pytest.raises(KmsEncryptionException):
        EncryptionService(provider, resolver).encrypt(b"payload")


def test_datakey_signing_and_verification(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    key = DataKeyService(provider, resolver).generate()
    assert key.plaintext_key == b"data-key"
    assert key.ciphertext_key == b"encrypted-key"

    signature = SigningService(provider, resolver).sign(b"payload")
    assert signature.signing_algorithm == "RSASSA_PSS_SHA_256"
    verifier = VerificationService(provider, resolver)
    assert verifier.verify(b"payload", signature.signature) is True
    assert verifier.verify(b"payload", b"invalid") is False
    with pytest.raises(KmsSigningException):
        verifier.verify(b"", b"signature")
    with pytest.raises(KmsSigningException):
        verifier.verify(b"payload", b"")
    with pytest.raises(KmsSigningException):
        SigningService(provider, resolver).sign(b"")


def test_provider_failure_during_verification_is_not_invalid_signature(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    provider.raise_error = True
    with pytest.raises(KmsSigningException):
        VerificationService(provider, resolver).verify(b"payload", b"signature")


def test_invalid_signature_provider_error_returns_false(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    def invalid_signature(**kwargs: object) -> dict[str, Any]:
        raise ClientError(
            {"Error": {"Code": "KMSInvalidSignatureException"}},
            "Verify",
        )

    provider.verify = invalid_signature  # type: ignore[method-assign]
    assert VerificationService(provider, resolver).verify(b"payload", b"invalid") is False


def test_secret_resolver_can_supply_kms_settings() -> None:
    class FakeSecretResolver(SecretResolver):
        def __init__(self, payload: object) -> None:
            self.payload = payload

        def resolve_json(
            self,
            name: str,
            *,
            version_id: str | None = None,
            version_stage: str | None = None,
            use_cache: bool = True,
        ) -> Any:
            return self.payload

    resolver = FakeSecretResolver(
        {
            "aws_region": "eu-west-1",
            "kms_key_alias": "alias/from-secret",
            "environment": "test",
        }
    )
    settings = KmsSettings.from_secret_resolver(resolver, secret_name="platform/kms")
    assert settings.aws_region == "eu-west-1"
    assert settings.key_identifier == "alias/from-secret"

    with pytest.raises(KmsConfigurationException):
        KmsSettings.from_secret_resolver(
            FakeSecretResolver({"kms_key_id": "key", "unexpected": "value"}),
            secret_name="platform/kms",
        )


def test_audit_metadata_contains_required_safe_fields() -> None:
    context = RequestContext(tenant_id="tenant-a")
    audit = KmsAuditMetadata.from_request(
        operation="encrypt",
        key_id="key-123",
        key_alias="alias/platform",
        account_id="123456789012",
        region="us-east-1",
        request_context=context,
    ).to_log_fields()
    assert audit["operation"] == "encrypt"
    assert audit["key_alias"] == "alias/platform"
    assert audit["key_id"] == "key-123"
    assert audit["account_id"] == "123456789012"
    assert audit["region"] == "us-east-1"
    assert audit["correlation_id"] == str(context.correlation_id)
    assert audit["trace_id"] == str(context.trace_id)
    assert audit["timestamp"] is not None


def test_structured_logger_redacts_cryptographic_material() -> None:
    logger = StructuredLogger("kms-test")
    sanitized = logger._build_entry(
        "kms_test",
        level="INFO",
        plaintext="plain",
        ciphertext="cipher",
        signature="sig",
        data_key="key",
        key_material="material",
        nested=[{"ciphertext": "nested-cipher"}],
    ).sanitize()
    assert sanitized.attributes == {
        "plaintext": "[REDACTED]",
        "ciphertext": "[REDACTED]",
        "signature": "[REDACTED]",
        "data_key": "[REDACTED]",
        "key_material": "[REDACTED]",
        "nested": [{"ciphertext": "[REDACTED]"}],
    }


def test_shared_kms_testing_factories_and_fake_provider() -> None:
    settings = build_kms_settings(region="eu-west-1")
    assert settings.aws_region == "eu-west-1"
    assert settings.key_identifier == "alias/test-key"

    provider = build_fake_kms_provider()
    assert provider.describe_key(key_id="alias/test-key")["KeyMetadata"]["KeyState"] == "Enabled"
    assert provider.encrypt(
        key_id="test-key",
        plaintext=b"plain",
        encryption_context={},
    )["CiphertextBlob"] == b"fake-ciphertext"
    assert provider.decrypt(
        ciphertext=b"cipher",
        encryption_context={},
    )["Plaintext"] == b"fake-plaintext"
    assert provider.generate_data_key(
        key_id="test-key",
        key_spec="AES_256",
        encryption_context={},
    )["CiphertextBlob"] == b"fake-encrypted-data-key"
    assert provider.sign(
        key_id="test-key",
        message=b"message",
        signing_algorithm="RSASSA_PSS_SHA_256",
    )["Signature"] == b"fake-signature"
    assert provider.verify(
        key_id="test-key",
        message=b"message",
        signature=b"fake-signature",
        signing_algorithm="RSASSA_PSS_SHA_256",
    )["SignatureValid"] is True
    assert provider.calls == [
        "describe_key",
        "encrypt",
        "decrypt",
        "generate_data_key",
        "sign",
        "verify",
    ]

    fixture_settings = kms_settings_fixture(signing_key_alias="alias/signing")
    assert fixture_settings.key_identifier_for_signing() == "alias/signing"
    shared_provider = SharedFakeKmsProvider()
    assert shared_provider.describe_key(key_id="test-key")["KeyMetadata"]["KeyId"] == "test-key"
    failing_provider = build_fake_kms_provider(error=RuntimeError("provider failure"))
    with pytest.raises(RuntimeError, match="provider failure"):
        failing_provider.describe_key(key_id="test-key")


def test_aws_provider_maps_only_approved_kms_operations() -> None:
    client = FakeBotoKmsClient()
    factory = FakeAwsClientFactory(client)
    provider = AwsKmsProvider(
        client_factory=factory,
        settings=KmsSettings(
            aws_region="eu-west-1",
            kms_key_alias="alias/test",
            endpoint_url="http://localhost:4566",
            environment="test",
        ),
    )

    assert provider.describe_key(key_id="alias/test")["operation"] == "describe_key"
    provider.encrypt(key_id="key", plaintext=b"p", encryption_context={"tenant_id": "t"})
    provider.decrypt(ciphertext=b"c", encryption_context={"tenant_id": "t"})
    provider.generate_data_key(
        key_id="key",
        key_spec="AES_256",
        encryption_context={"tenant_id": "t"},
    )
    provider.sign(key_id="key", message=b"m", signing_algorithm="RSASSA_PSS_SHA_256")
    provider.verify(
        key_id="key",
        message=b"m",
        signature=b"s",
        signing_algorithm="RSASSA_PSS_SHA_256",
    )

    assert factory.options["service_name"] == "kms"
    assert factory.options["region_name"] == "eu-west-1"
    assert factory.options["endpoint_url"] == "http://localhost:4566"
    assert [operation for operation, _ in client.calls] == [
        "describe_key",
        "encrypt",
        "decrypt",
        "generate_data_key",
        "sign",
        "verify",
    ]
    assert client.calls[-2][1]["MessageType"] == "RAW"
    assert client.calls[-1][1]["MessageType"] == "RAW"
    assert not hasattr(provider, "create_key")
    assert not hasattr(provider, "put_key_policy")


def test_resolver_rejects_incomplete_and_cross_account_key_metadata(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    with pytest.raises(KmsValidationException):
        resolver.resolve(" ", KeyPurpose.ENCRYPTION)
    provider.describe_response = {}
    with pytest.raises(KmsValidationException):
        resolver.resolve(None, KeyPurpose.ENCRYPTION)

    provider.describe_response = {"KeyMetadata": {"KeyId": "key"}}
    with pytest.raises(KmsValidationException):
        resolver.resolve(None, KeyPurpose.ENCRYPTION)

    provider.describe_response = {
        "KeyMetadata": {
            "KeyId": "key-123",
            "Arn": "arn:aws:kms:us-east-1:999999999999:key/key-123",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeyState": "Enabled",
        }
    }
    account_checked_resolver = KmsKeyResolver(
        provider,
        KmsSettings(
            account_id="123456789012",
            kms_key_id="key-123",
            environment="test",
        ),
    )
    with pytest.raises(KmsValidationException):
        account_checked_resolver.resolve(None, KeyPurpose.ENCRYPTION)


def test_resolver_facade_and_health_validators(
    kms: tuple[FakeKmsProvider, KmsKeyResolver],
) -> None:
    provider, resolver = kms
    facade = KmsResolver(provider, KmsSettings(kms_key_alias="alias/test", environment="test"))
    assert facade.resolve(None, KeyPurpose.ENCRYPTION).key_id == "key-123"
    assert KmsHealthCheck(resolver).is_healthy() is True
    assert KmsConnectionValidator(resolver).validate() is True
