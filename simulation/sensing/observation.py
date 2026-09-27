"""The typed observation object.

An Observation is the only channel through which sensing information may
reach an agent's estimator. It carries enough provenance to say, later,
exactly which agent produced it, when, and under what measurement
uncertainty.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Observation:
    """A single sensor measurement, addressed to a specific agent.

    Parameters
    ----------
    agent_id:
        The agent this measurement belongs to.
    timestamp:
        Simulation time, from SimulationClock, at which the measurement
        was taken.
    value:
        The measured value, as a NumPy array.
    covariance:
        The measurement noise covariance associated with this observation.
        Must be square, symmetric, and match the dimension of value.
    """

    agent_id: str
    timestamp: float
    value: np.ndarray
    covariance: np.ndarray

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise ValueError("Observation.agent_id must be a non-empty string")
        if not math.isfinite(self.timestamp):
            raise ValueError(f"Observation.timestamp must be finite, got {self.timestamp!r}")
        value = np.asarray(self.value, dtype=float)
        covariance = np.asarray(self.covariance, dtype=float)
        if value.ndim != 1:
            raise ValueError(f"Observation.value must be one dimensional, got shape {value.shape}")
        if not np.all(np.isfinite(value)):
            raise ValueError("Observation.value must be finite")
        d = value.shape[0]
        if covariance.shape != (d, d):
            raise ValueError(
                f"Observation.covariance must have shape ({d}, {d}) to match value, "
                f"got {covariance.shape}"
            )
        if not np.allclose(covariance, covariance.T):
            raise ValueError("Observation.covariance must be symmetric")
        if not np.all(np.isfinite(covariance)):
            raise ValueError("Observation.covariance must be finite")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "covariance", covariance)
