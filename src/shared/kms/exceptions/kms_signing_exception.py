"""KMS signing and verification failure."""

from shared.kms.exceptions.kms_exception import KmsException


class KmsSigningException(KmsException):
    """Raised when KMS cannot sign or verify a message."""
