"""Serialize secret payloads into safe JSON or text."""

from __future__ import annotations

import json
from typing import Any


class SecretSerializer:
    """Serialize secret payloads without exposing them in logs."""

    def serialize(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
