"""Archive metadata for future EventBridge retention support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArchiveMetadata:
    """Store archive enablement and retention configuration without implementing backup storage."""

    archive_enabled: bool = False
    retention_days: int = 30
