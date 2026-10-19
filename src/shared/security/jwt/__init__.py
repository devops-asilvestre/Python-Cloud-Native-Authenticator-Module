"""JWT issuance and validation contract; no JWT implementation is included."""

from collections.abc import Mapping
from datetime import datetime
from typing import Protocol


class JwtService(Protocol):
    """Adapter contract for signing and validating JWTs."""

    def sign(self, claims: Mapping[str, object], *, expires_at: datetime) -> str: ...

    def verify(
        self,
        token: str,
        *,
        audience: str,
        issuer: str,
    ) -> Mapping[str, object]: ...
