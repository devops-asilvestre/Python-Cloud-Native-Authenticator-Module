"""Metadata describing secret rotation status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SecretRotationMetadata:
    """Rotation metadata for a managed secret."""

    rotation_enabled: bool = False
    rotation_days: int | None = None
    last_rotated_at: datetime | None = None
    next_rotation_at: datetime | None = None
    rotation_lambda_arn: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "rotation_enabled": self.rotation_enabled,
            "rotation_days": self.rotation_days,
            "last_rotated_at": (
                self.last_rotated_at.isoformat() if self.last_rotated_at else None
            ),
            "next_rotation_at": (
                self.next_rotation_at.isoformat() if self.next_rotation_at else None
            ),
            "rotation_lambda_arn": self.rotation_lambda_arn,
        }
