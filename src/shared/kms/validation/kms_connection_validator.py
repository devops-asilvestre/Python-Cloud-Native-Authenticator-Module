"""KMS connection validator."""

from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.kms.validation.kms_health_check import KmsHealthCheck


class KmsConnectionValidator:
    """Validate KMS connectivity and configured key metadata."""

    def __init__(self, resolver: KmsKeyResolver) -> None:
        self._health_check = KmsHealthCheck(resolver)

    def validate(self, *, purpose: KeyPurpose = KeyPurpose.ENCRYPTION) -> bool:
        return self._health_check.is_healthy(purpose=purpose)
