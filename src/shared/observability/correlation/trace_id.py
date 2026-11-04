"""Trace identifier value object."""

from __future__ import annotations

from shared.observability.correlation.uuidv7 import UUIDv7


class TraceId(UUIDv7):
    """UUIDv7 generated trace value."""

    __slots__ = ()
