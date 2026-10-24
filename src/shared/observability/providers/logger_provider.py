"""Abstract logger provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from shared.observability.logging.logger_contract import LoggerContract


class LoggerProvider(ABC):
    """Abstract factory for structured loggers."""

    @abstractmethod
    def get_logger(self, name: str) -> LoggerContract: ...
