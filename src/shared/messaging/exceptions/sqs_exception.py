"""Exceptions raised by the shared messaging foundation."""


class SqsException(Exception):
    """Base exception for messaging operations."""


class SqsConfigurationException(SqsException, ValueError):
    """Invalid SQS runtime configuration."""


class MessagePublishException(SqsException):
    """A message could not be published."""


class MessageConsumeException(SqsException):
    """A message could not be received or decoded."""


class IdempotencyException(SqsException):
    """An idempotency operation failed."""
