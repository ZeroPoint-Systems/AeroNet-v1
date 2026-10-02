from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class State2D:
    x: float
    y: float


@dataclass
class Estimate:
    state: State2D
    covariance: np.ndarray

    @property
    def covariance_trace(self) -> float:
        return float(np.trace(self.covariance))


@dataclass
class Observation:
    agent_id: int
    time: float
    truth: State2D
    measured: State2D


@dataclass
class Packet:
    time_sent: float
    time_delivered: Optional[float]
    sender: int
    receiver: int
    delivered: bool
    latency: float
    estimate: Estimate


@dataclass
class Agent:
    agent_id: int
    position: State2D
    estimate: Estimate


@dataclass
class SimulationResult:
    observations: list[Observation] = field(default_factory=list)
    packets: list[Packet] = field(default_factory=list)
    trajectory: list[dict] = field(default_factory=list)
