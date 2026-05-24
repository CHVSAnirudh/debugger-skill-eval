"""Rolling-window statistics with cache invalidation.

Computes mean / max / min over the last `window_size` measurements.
Used by the dashboard module to render live stats.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass
class Measurement:
    timestamp: float
    value: float


class RollingStats:
    """Maintains rolling mean/max/min over a sliding window of values.

    Internal caches are invalidated lazily for performance: we only recompute
    max/min when the rolling window evicts the current extremum.
    """

    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self.window_size = window_size
        self._values: list[float] = []
        self._cached_mean: float | None = None
        self._cached_max: float | None = None
        self._cached_min: float | None = None

    def add(self, value: float) -> None:
        self._values.append(value)
        popped: float | None = None
        if len(self._values) > self.window_size:
            popped = self._values.pop(0)

        # Mean must always be recomputed when the window changes.
        self._cached_mean = None

        # Max/min caches are only invalidated when the evicted value WAS the
        # cached extremum. Otherwise they remain valid (other values are still
        # in the window, and the current cached extremum is still <=/>= them).
        if popped is not None:
            if self._cached_max is not None and popped == self._cached_max:
                self._cached_max = None
            if self._cached_min is not None and popped == self._cached_min:
                self._cached_min = None

    def mean(self) -> float:
        if not self._values:
            raise ValueError("no values")
        if self._cached_mean is None:
            self._cached_mean = sum(self._values) / len(self._values)
        return self._cached_mean

    def max(self) -> float:
        if not self._values:
            raise ValueError("no values")
        if self._cached_max is None:
            self._cached_max = max(self._values)
        return self._cached_max

    def min(self) -> float:
        if not self._values:
            raise ValueError("no values")
        if self._cached_min is None:
            self._cached_min = min(self._values)
        return self._cached_min

    def snapshot(self) -> dict:
        return {
            "n": len(self._values),
            "mean": round(self.mean(), 4),
            "max": self.max(),
            "min": self.min(),
        }


class Dashboard:
    """Aggregates multiple named RollingStats streams."""

    def __init__(self, window_size: int):
        self._streams: dict[str, RollingStats] = {}
        self._window = window_size

    def ingest(self, stream: str, measurement: Measurement) -> None:
        if stream not in self._streams:
            self._streams[stream] = RollingStats(self._window)
        self._streams[stream].add(measurement.value)

    def render(self) -> dict:
        return {name: stats.snapshot() for name, stats in self._streams.items()}


def process(events: list[dict], window_size: int) -> dict:
    """Top-level entry point. Each event is {stream, timestamp, value}."""
    dash = Dashboard(window_size)
    for ev in events:
        dash.ingest(ev["stream"], Measurement(ev["timestamp"], ev["value"]))
    return dash.render()


def _format_output(result: dict) -> str:
    parts = []
    for stream in sorted(result):
        s = result[stream]
        parts.append(
            f"{stream}: n={s['n']} mean={s['mean']} max={s['max']} min={s['min']}"
        )
    return "\n".join(parts)


if __name__ == "__main__":
    data = json.load(sys.stdin)
    dash = Dashboard(data["window_size"])
    # Render after each event so the live dashboard sees current stats. The
    # final render shows the steady-state snapshot.
    for ev in data["events"]:
        dash.ingest(ev["stream"], Measurement(ev["timestamp"], ev["value"]))
        dash.render()
    print(_format_output(dash.render()))
