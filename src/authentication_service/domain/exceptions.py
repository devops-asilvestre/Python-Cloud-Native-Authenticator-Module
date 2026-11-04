class AuthenticationDomainError(ValueError):
    """Base error for the authentication bounded context."""


class InvalidPassword(AuthenticationDomainError):
    pass


class CredentialNotFound(AuthenticationDomainError):
    pass


class AuthenticationBlocked(AuthenticationDomainError):
    pass


class InvalidCredentialState(AuthenticationDomainError):
    pass


class SessionNotFound(AuthenticationDomainError):
    pass
