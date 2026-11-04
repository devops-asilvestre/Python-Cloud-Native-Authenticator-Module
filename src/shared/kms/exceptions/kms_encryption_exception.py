"""KMS encryption failure."""

from shared.kms.exceptions.kms_exception import KmsException


class KmsEncryptionException(KmsException):
    """Raised when KMS cannot encrypt or generate a data key."""
