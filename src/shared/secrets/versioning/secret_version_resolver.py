"""Resolve the appropriate version and stage for a secret."""

from __future__ import annotations

from typing import Any


class SecretVersionResolver:
    """Helpers to resolve version ids or version stages for AWS-backed secrets."""

    @staticmethod
    def resolve(
        *,
        response: dict[str, Any] | None = None,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> tuple[str | None, str | None]:
        candidate_version_id = version_id or (response or {}).get("VersionId")
        candidate_version_stage = version_stage or (response or {}).get("VersionStage")
        if response and not candidate_version_stage:
            stages = response.get("VersionStages")
            if isinstance(stages, list) and stages:
                candidate_version_stage = str(stages[0])
        return candidate_version_id, candidate_version_stage

    @staticmethod
    def normalize_version_stage(version_stage: str | None) -> str:
        return version_stage or "AWSCURRENT"
