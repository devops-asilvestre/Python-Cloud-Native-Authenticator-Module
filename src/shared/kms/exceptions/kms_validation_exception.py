"""Invalid KMS input or key configuration."""

from shared.kms.exceptions.kms_exception import KmsException


class KmsValidationException(KmsException):
    """Raised when KMS input, tenant context, or key metadata is invalid."""
