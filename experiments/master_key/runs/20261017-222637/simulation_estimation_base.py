"""The estimator interface.

Every estimator used anywhere in AeroNet, whether a local filter, a
distributed filter, a covariance intersection fusion rule, or the
centralised oracle used only as a reference bound, implements this same
interface. This is what allows estimators to be swapped and compared
without changing any other part of the simulator.

An estimator never receives the true state directly. It only ever receives
an Observation, through update(), or a peer's published mean and
covariance, through incorporate_peer_estimate().
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

from simulation.sensing.observation import Observation


class Estimator(Protocol):
    """The interface every estimator implementation must satisfy."""

    def predict(self, dt: float) -> None:
        """Advance the estimate through the process model by dt."""
        ...

    def update(self, observation: Observation) -> None:
        """Incorporate a direct measurement."""
        ...

    def incorporate_peer_estimate(
        self, sender_id: str, mean: np.ndarray, covariance: np.ndarray
    ) -> None:
        """Incorporate an estimate received from another agent.

        This is the step where naively averaging correlated estimates would
        silently produce an overconfident fused uncertainty. Implementations
        must either use a fusion rule whose consistency properties are
        established in the literature, or must refuse to fuse and say so
        explicitly, rather than default to a plain average. See
        simulation/estimation/covariance_intersection.py.
        """
        ...

    def estimate(self) -> np.ndarray:
        """The current state estimate."""
        ...

    def covariance(self) -> np.ndarray:
        """The current estimate covariance."""
        ...
