"""KMS decryption failure."""

from shared.kms.exceptions.kms_exception import KmsException


class KmsDecryptionException(KmsException):
    """Raised when KMS cannot decrypt a ciphertext."""
