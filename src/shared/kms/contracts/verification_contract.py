"""Signature verification service contract."""

from __future__ import annotations

from typing import Protocol


class VerificationContract(Protocol):
    """Verify a message signature through the shared KMS foundation."""

    def verify(self, payload: bytes, signature: bytes) -> bool: ...
