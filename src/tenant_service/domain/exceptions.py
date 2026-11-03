class TenantDomainError(ValueError):
    """Base error for invalid tenant business data."""


class InvalidTenantTransition(TenantDomainError):
    """Raised when a tenant lifecycle transition is not allowed."""


class TenantNotFound(TenantDomainError):
    """Raised when a tenant cannot be found."""


class TenantAlreadyExists(TenantDomainError):
    """Raised when a unique tenant attribute is already in use."""


class IdempotencyConflict(TenantDomainError):
    """Raised when a key is reused with a different request."""
