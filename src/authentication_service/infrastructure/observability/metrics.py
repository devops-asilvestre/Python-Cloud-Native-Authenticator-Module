from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram


class OpenTelemetryAuthenticationMetrics:
    def __init__(self) -> None:
        meter = metrics.get_meter("authentication-service")
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._meter = meter

    def observe(self, name: str, value: float, **attributes: str) -> None:
        if name.endswith("duration_ms"):
            histogram = self._histograms.get(name)
            if histogram is None:
                histogram = self._meter.create_histogram(name, unit="ms")
                self._histograms[name] = histogram
            histogram.record(value, attributes)
            return
        counter = self._counters.get(name)
        if counter is None:
            counter = self._meter.create_counter(name)
            self._counters[name] = counter
        counter.add(value, attributes)
