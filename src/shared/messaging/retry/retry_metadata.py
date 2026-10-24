"""Metadata used to calculate a retry decision."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryMetadata:
    """Attempt count and retry limits for one message."""

    attempt: int
    max_attempts: int

    def __post_init__(self) -> None:
        if self.attempt < 1 or self.max_attempts < 1:
            raise ValueError("Retry attempt and maximum attempts must be positive.")
