"""Deterministic simulation clock.

The simulator never uses wall clock time. Every notion of time inside a
simulation run is derived from a fixed step size and a step counter, so
that a run can be paused, resumed, or reproduced exactly without depending
on how long the computation actually took.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class SimulationClock:
    """A deterministic clock advancing in fixed steps of size dt.

    The invariant time == step_index * dt is checked on every read and
    after every step, rather than assumed.
    """

    dt: float
    step_index: int = 0

    def __post_init__(self) -> None:
        if not math.isfinite(self.dt) or self.dt <= 0.0:
            raise ValueError(f"dt must be a finite positive number, got {self.dt!r}")
        if self.step_index < 0:
            raise ValueError(f"step_index must not be negative, got {self.step_index!r}")

    @property
    def time(self) -> float:
        return self.step_index * self.dt

    def step(self) -> float:
        """Advance the clock by one step and return the new time."""
        self.step_index += 1
        return self.time

    def reset(self) -> None:
        """Return the clock to step zero, time zero."""
        self.step_index = 0
