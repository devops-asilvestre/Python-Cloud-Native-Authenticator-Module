"""Base exception for domain-layer errors."""

from typing import ClassVar


class DomainException(Exception):
    """Base for explicit domain errors; concrete errors belong to each domain."""

    error_code: ClassVar[str] = "domain_error"
