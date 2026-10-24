"""Invalid KMS configuration."""

from shared.kms.exceptions.kms_exception import KmsException


class KmsConfigurationException(KmsException):
    """Raised when KMS configuration is missing or invalid."""
