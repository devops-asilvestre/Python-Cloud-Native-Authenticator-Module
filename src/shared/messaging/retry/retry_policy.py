"""Bounded exponential retry policy."""

from dataclasses import dataclass
from math import pow

from shared.events.exceptions.event_exception import EventException
from shared.messaging.retry.retry_metadata import RetryMetadata


@dataclass(frozen=True, slots=True)
class RetryDecision:
    """Retry or dead-letter outcome with a recommended backoff."""

    should_retry: bool
    should_dead_letter: bool
    delay_seconds: int
    attempt: int


class RetryPolicy:
    """Calculate capped exponential backoff and stop on permanent failures."""

    def __init__(
        self,
        *,
        max_attempts: int = 5,
        base_delay_seconds: int = 1,
        max_delay_seconds: int = 300,
    ) -> None:
        if max_attempts < 1 or base_delay_seconds < 1 or max_delay_seconds < 1:
            raise ValueError("Retry limits and delays must be positive.")
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds

    def evaluate(self, error: Exception, metadata: RetryMetadata) -> RetryDecision:
        permanent = isinstance(error, EventException)
        dead_letter = permanent or metadata.attempt >= min(metadata.max_attempts, self.max_attempts)
        delay = min(
            int(self.base_delay_seconds * pow(2, metadata.attempt - 1)),
            self.max_delay_seconds,
        )
        return RetryDecision(
            should_retry=not dead_letter,
            should_dead_letter=dead_letter,
            delay_seconds=0 if dead_letter else delay,
            attempt=metadata.attempt,
        )
