"""Request identifier value object."""

from __future__ import annotations

from shared.observability.correlation.uuidv7 import UUIDv7


class RequestId(UUIDv7):
    """UUIDv7 generated request value."""

    __slots__ = ()
