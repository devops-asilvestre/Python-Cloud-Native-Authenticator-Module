"""Value object representing a resolved secret payload."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.masking.secret_masking_utility import SecretMaskingUtility


@dataclass(frozen=True, slots=True)
class SecretContract:
    """Resolved secret value with metadata and safe masking support."""

    name: str
    value: str
    version: str | None = None
    region: str = "us-east-1"
    account_id: str | None = None
    metadata: SecretMetadata | None = None
    source: str = "aws-secrets-manager"
    tags: dict[str, str] = field(default_factory=dict)

    def masked_value(self) -> str:
        return SecretMaskingUtility.mask(self.value)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "region": self.region,
            "account_id": self.account_id,
            "source": self.source,
            "value": self.masked_value(),
        }
        if self.metadata is not None:
            payload["metadata"] = self.metadata.as_dict()
        if self.tags:
            payload["tags"] = dict(self.tags)
        return payload

    def __str__(self) -> str:
        return (
            f"SecretContract(name={self.name!r}, version={self.version!r}, "
            f"region={self.region!r}, account_id={self.account_id!r}, "
            f"value={self.masked_value()!r})"
        )
