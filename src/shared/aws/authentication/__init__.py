"""Authentication helpers for AWS."""

from shared.aws.authentication.credential_resolver import AwsCredentialResolver
from shared.aws.authentication.identity_resolver import AwsIdentityResolver

__all__ = ["AwsCredentialResolver", "AwsIdentityResolver"]
