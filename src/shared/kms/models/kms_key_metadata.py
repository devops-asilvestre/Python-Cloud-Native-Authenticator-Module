"""Metadata for a resolved KMS key."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KmsKeyMetadata:
    """Non-secret metadata returned after validating a KMS key."""

    key_id: str
    arn: str
    key_usage: str
    key_state: str
    region: str
    account_id: str | None
    key_alias: str | None = None
