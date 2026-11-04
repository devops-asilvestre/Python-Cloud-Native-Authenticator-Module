"""Digital signature value model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DigitalSignature:
    """Signature bytes and non-secret verification metadata."""

    signature: bytes
    key_id: str
    signing_algorithm: str
