"""JSON serializer for Redis cache values."""

from __future__ import annotations

import json
from typing import Any


class JsonSerializer:
    """Serialize primitive and structured values as JSON for cache transport."""

    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def loads(raw: str | bytes | bytearray | None) -> Any:
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            return json.loads(raw.decode("utf-8"))
        return json.loads(raw)

    @staticmethod
    def encode(value: Any) -> str:
        return JsonSerializer.dumps(value)

    @staticmethod
    def decode(raw: str | bytes | bytearray | None) -> Any:
        return JsonSerializer.loads(raw)
