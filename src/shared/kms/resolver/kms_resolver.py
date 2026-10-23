"""Convenience resolver for KMS key metadata."""

from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.models.kms_key_metadata import KmsKeyMetadata
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.kms.settings.kms_settings import KmsSettings


class KmsResolver:
    """Expose the configured key resolver as a foundation-level dependency."""

    def __init__(self, provider: KmsProviderContract, settings: KmsSettings) -> None:
        self._resolver = KmsKeyResolver(provider, settings)

    def resolve(self, tenant_id: str | None, purpose: KeyPurpose) -> KmsKeyMetadata:
        return self._resolver.resolve(tenant_id, purpose)
