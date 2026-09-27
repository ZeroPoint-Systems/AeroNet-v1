"""Observation models.

An observation model implements z = h(x, p) + v, where x is the hidden
state, p is the observing agent's position, h is the deterministic part
of the measurement, and v is measurement noise drawn from an explicit
noise model.

Sprint 1 uses the simplest possible model, z = x + v, with a fixed
covariance R that does not depend on agent position. This is a controlled
baseline, not a claim about how any real UAV sensor behaves. A
geometry-dependent model, R = R(p, x), is introduced later, once the
static, geometry-free case has been validated. See theory/sensing_model.md
and theory/geometry_model.md for the research-level discussion.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

from simulation.core.state import State2D
from simulation.sensing.noise import GaussianNoise
from simulation.sensing.observation import Observation


class ObservationModel(Protocol):
    """The interface every observation model must satisfy."""

    def observe(
        self,
        agent_id: str,
        agent_position: State2D,
        true_state: State2D,
        timestamp: float,
    ) -> Observation:
        ...


class DirectGaussianObservationModel:
    """z = x + v, v ~ N(0, R), with R fixed and independent of position.

    ASSUMPTION: the measurement does not depend on the observing agent's
    position or on the true state. This is a deliberately simplified
    baseline used to validate the estimation and communication machinery
    before geometry-dependent sensing is introduced.
    """

    def __init__(self, measurement_covariance: np.ndarray, rng: np.random.Generator) -> None:
        self._noise = GaussianNoise(covariance=measurement_covariance, rng=rng)

    def observe(
        self,
        agent_id: str,
        agent_position: State2D,
        true_state: State2D,
        timestamp: float,
    ) -> Observation:
        value = true_state.as_array() + self._noise.sample()
        return Observation(
            agent_id=agent_id,
            timestamp=timestamp,
            value=value,
            covariance=self._noise.covariance,
        )
