"""Base AWS-specific exception."""

from __future__ import annotations


class AwsException(RuntimeError):
    """Base exception for AWS foundation failures."""
