"""Exponential backoff policy for EventBridge transient failures."""

from __future__ import annotations

from dataclasses import dataclass
from math import pow
from random import uniform

from shared.eventbus.retry.retry_metadata import RetryMetadata


@dataclass(frozen=True, slots=True)
class RetryDecision:
    """Outcome for a retryable EventBridge publication failure."""

    should_retry: bool
    should_dead_letter: bool
    delay_seconds: int
    attempt: int


class RetryPolicy:
    """Bounded exponential backoff with jitter-aware delay selection."""

    def __init__(
        self,
        *,
        max_attempts: int = 5,
        base_delay_seconds: int = 1,
        max_delay_seconds: int = 300,
        jitter_ratio: float = 0.2,
    ) -> None:
        if max_attempts < 1 or base_delay_seconds < 1 or max_delay_seconds < 1:
            raise ValueError("Retry limits and delays must be positive.")
        if not 0 <= jitter_ratio <= 1:
            raise ValueError("Retry jitter ratio must be between 0 and 1.")
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.jitter_ratio = jitter_ratio

    def evaluate(self, error: Exception, metadata: RetryMetadata) -> RetryDecision:
        _ = error
        attempt_limit = min(metadata.max_attempts, self.max_attempts)
        should_retry = metadata.attempt < attempt_limit
        delay = min(
            int(self.base_delay_seconds * pow(2, max(0, metadata.attempt - 1))),
            self.max_delay_seconds,
        )
        if should_retry and self.jitter_ratio:
            delay = min(
                self.max_delay_seconds,
                max(1, int(delay * uniform(1 - self.jitter_ratio, 1 + self.jitter_ratio))),
            )
        return RetryDecision(
            should_retry=should_retry,
            should_dead_letter=not should_retry,
            delay_seconds=delay if should_retry else 0,
            attempt=metadata.attempt,
        )
