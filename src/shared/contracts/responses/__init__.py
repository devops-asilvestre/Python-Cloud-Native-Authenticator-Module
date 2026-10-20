"""Generic response envelopes."""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BaseResponse[T]:
    """Successful response data with optional non-sensitive metadata."""

    data: T
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ErrorResponse:
    """Stable error envelope without exception details or stack traces."""

    code: str
    message: str
    details: Mapping[str, object] = field(default_factory=dict)
