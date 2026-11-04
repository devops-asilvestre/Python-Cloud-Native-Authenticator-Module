"""Raised when AWS credentials or identity cannot be resolved."""

from __future__ import annotations

from shared.aws.exceptions.aws_exception import AwsException


class AwsAuthenticationException(AwsException):
    """Raised when AWS authentication cannot be established."""
