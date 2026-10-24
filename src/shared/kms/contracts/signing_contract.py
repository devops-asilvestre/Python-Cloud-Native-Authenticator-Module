"""Signing service contract."""

from __future__ import annotations

from typing import Protocol

from shared.kms.models.digital_signature import DigitalSignature


class SigningContract(Protocol):
    """Sign a message through the shared KMS foundation."""

    def sign(self, payload: bytes) -> DigitalSignature: ...
