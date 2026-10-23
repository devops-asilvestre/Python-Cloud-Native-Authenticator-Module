"""KMS key availability check."""

from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver


class KmsHealthCheck:
    """Validate that the configured KMS key is enabled and usable."""

    def __init__(self, resolver: KmsKeyResolver) -> None:
        self._resolver = resolver

    def is_healthy(self, *, purpose: KeyPurpose = KeyPurpose.ENCRYPTION) -> bool:
        self._resolver.resolve(None, purpose)
        return True
