"""Abstract metrics provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from shared.observability.metrics.counter_contract import CounterContract
from shared.observability.metrics.gauge_contract import GaugeContract
from shared.observability.metrics.histogram_contract import HistogramContract


class MetricsProvider(ABC):
    """Abstract factory for metric contracts."""

    @abstractmethod
    def counter(self, name: str, *, help_text: str, unit: str = "count") -> CounterContract: ...

    @abstractmethod
    def gauge(self, name: str, *, help_text: str, unit: str = "count") -> GaugeContract: ...

    @abstractmethod
    def histogram(self, name: str, *, help_text: str, unit: str = "count") -> HistogramContract: ...
