import re
from dataclasses import dataclass

from tenant_service.domain.exceptions import TenantDomainError


@dataclass(frozen=True, slots=True)
class TenantSettings:
    timezone: str = "UTC"
    language: str = "en"
    country: str = "US"
    currency: str = "USD"
    branding_enabled: bool = False
    audit_enabled: bool = True
    mfa_required: bool = False

    def __post_init__(self) -> None:
        for field in ("timezone", "language", "country", "currency"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise TenantDomainError(f"{field} must be a non-empty string.")
            object.__setattr__(self, field, value.strip())
        if (
            re.fullmatch(r"[A-Za-z]{2,10}(?:-[A-Za-z]{2,4})?", self.language) is None
            or re.fullmatch(r"[A-Za-z]{2}", self.country) is None
            or re.fullmatch(r"[A-Z]{3}", self.currency.upper()) is None
        ):
            raise TenantDomainError("Tenant locale and currency values have invalid formats.")
        for field in ("branding_enabled", "audit_enabled", "mfa_required"):
            if not isinstance(getattr(self, field), bool):
                raise TenantDomainError(f"{field} must be a boolean.")
        object.__setattr__(self, "language", self.language.lower())
        object.__setattr__(self, "country", self.country.upper())
        object.__setattr__(self, "currency", self.currency.upper())
