"""Raised when AWS configuration is invalid or incomplete."""

from __future__ import annotations

from shared.aws.exceptions.aws_exception import AwsException


class AwsConfigurationException(AwsException):
    """Raised when the AWS configuration is missing or invalid."""
