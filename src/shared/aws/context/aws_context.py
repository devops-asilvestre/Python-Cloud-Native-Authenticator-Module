"""Context information describing the active AWS identity and environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AwsContext:
    """Container for AWS identity and environment metadata."""

    account_id: str | None = None
    region: str | None = None
    profile: str | None = None
    role_arn: str | None = None
    arn: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "account_id": self.account_id,
            "region": self.region,
            "profile": self.profile,
            "role_arn": self.role_arn,
            "arn": self.arn,
            "user_id": self.user_id,
        }
        payload.update(self.metadata)
        return payload
