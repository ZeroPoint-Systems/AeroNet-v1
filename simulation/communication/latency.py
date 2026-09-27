"""Latency model.

Sprint 1 uses a fixed latency for every delivered packet. A random latency
distribution is a documented later extension, not implemented here, so
that the fixed case can be validated first.
"""

from __future__ import annotations

import math


class FixedLatencyModel:
    """Every delivered packet arrives exactly `latency` seconds after it
    was created.
    """

    def __init__(self, latency: float) -> None:
        if not math.isfinite(latency) or latency < 0:
            raise ValueError(f"latency must be finite and non-negative, got {latency!r}")
        self.latency = latency

    def delivery_time(self, created_time: float) -> float:
        return created_time + self.latency
