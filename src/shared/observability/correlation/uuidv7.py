"""UUIDv7 implementation used across observability identifiers."""

import secrets
import time
import uuid
from typing import Any, Self

from pydantic_core import core_schema


def _generate_uuid7() -> uuid.UUID:
    timestamp_ms = int(time.time_ns() // 1_000_000)
    value = bytearray(16)
    value[0:6] = timestamp_ms.to_bytes(6, byteorder="big")
    value[6:10] = secrets.token_bytes(4)
    value[10:16] = secrets.token_bytes(6)
    value[6] = (value[6] & 0x0F) | 0x70
    value[8] = (value[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(value))


class UUIDv7(str):
    """String representation of a UUIDv7 identifier."""

    def __new__(cls, value: str | None = None) -> Self:
        candidate = str(_generate_uuid7()) if value is None else str(value)
        parsed = uuid.UUID(candidate)
        if parsed.version != 7:
            raise ValueError(f"Expected a UUIDv7 value, got '{candidate}'.")
        return str.__new__(cls, str(parsed))

    @classmethod
    def generate(cls) -> Self:
        """Generate a new UUIDv7 value."""

        return cls(str(_generate_uuid7()))

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
        )
