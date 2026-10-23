"""Metadata describing a secret stored in AWS Secrets Manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SecretMetadata:
    """Optimized metadata for audit, rotation, and observability use cases."""

    name: str
    arn: str | None = None
    description: str | None = None
    version_id: str | None = None
    version_stage: str | None = None
    secret_type: str = "string"
    created_date: datetime | None = None
    last_changed_date: datetime | None = None
    last_accessed_date: datetime | None = None
    tags: dict[str, str] = field(default_factory=dict)
    rotation_enabled: bool = False
    rotation_lambda_arn: str | None = None
    owning_service: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "arn": self.arn,
            "description": self.description,
            "version_id": self.version_id,
            "version_stage": self.version_stage,
            "secret_type": self.secret_type,
            "created_date": (
                self.created_date.isoformat() if self.created_date else None
            ),
            "last_changed_date": (
                self.last_changed_date.isoformat() if self.last_changed_date else None
            ),
            "last_accessed_date": (
                self.last_accessed_date.isoformat() if self.last_accessed_date else None
            ),
            "rotation_enabled": self.rotation_enabled,
            "rotation_lambda_arn": self.rotation_lambda_arn,
            "owning_service": self.owning_service,
        }
        if self.tags:
            payload["tags"] = dict(self.tags)
        return payload
