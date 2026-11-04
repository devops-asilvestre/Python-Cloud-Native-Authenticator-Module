"""Deserialize secret payloads into JSON or plain text."""

from __future__ import annotations

import json
from typing import Any


class SecretDeserializer:
    """Deserialize JSON or plain-text secret payloads."""

    def deserialize(self, value: str) -> Any:
        if not value:
            return value
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
