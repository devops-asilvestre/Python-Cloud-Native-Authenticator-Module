class IdentityDomainError(ValueError):
    """Base error for the Identity Directory bounded context."""


class UserNotFound(IdentityDomainError):
    pass


class UserAlreadyExists(IdentityDomainError):
    pass


class InvalidUserTransition(IdentityDomainError):
    pass


class IdempotencyConflict(IdentityDomainError):
    pass


class TenantNotFound(IdentityDomainError):
    pass
