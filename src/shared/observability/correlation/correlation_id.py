"""Correlation identifier value object."""

from __future__ import annotations

from shared.observability.correlation.uuidv7 import UUIDv7


class CorrelationId(UUIDv7):
    """UUIDv7 generated correlation value.

    This identifier is used to group multiple logs and events that belong to the
    same user request or cross-service flow.
    """

    __slots__ = ()
