"""Reference linear Gaussian Kalman filter.

This is a local-only estimator, intentionally. It implements the standard
prediction and update equations for

    x_{k+1} = x_k + w_k,   w_k ~ N(0, Q)
    z_k     = H x_k + v_k, v_k ~ N(0, R)

with H fixed to the identity, consistent with the sprint 1 observation
model in simulation/sensing/observation_model.py. Its behaviour is
analytically predictable, which is what makes it useful as a reference
implementation to validate against, before any more elaborate estimator is
introduced.

It deliberately does not fuse peer estimates. See incorporate_peer_estimate
below and simulation/estimation/covariance_intersection.py.
"""

from __future__ import annotations

import numpy as np


class ReferenceKalmanFilter:
    """A local, single-agent linear Gaussian Kalman filter.

    Parameters
    ----------
    initial_mean:
        The prior mean, x_0.
    initial_covariance:
        The prior covariance, P_0. Should be large relative to the
        expected measurement noise if no informative prior is available,
        rather than arbitrarily small.
    process_noise_covariance:
        Q, the process noise covariance added at every predict() call.
        ASSUMPTION: for a genuinely static hidden state, Q should be the
        zero matrix; a small positive Q is sometimes used in practice to
        keep the filter from becoming overconfident, but that is a
        modelling choice that must be stated, not left implicit.
    """

    def __init__(
        self,
        initial_mean: np.ndarray,
        initial_covariance: np.ndarray,
        process_noise_covariance: np.ndarray,
    ) -> None:
        self._mean = np.asarray(initial_mean, dtype=float).copy()
        self._covariance = np.asarray(initial_covariance, dtype=float).copy()
        self._process_noise = np.asarray(process_noise_covariance, dtype=float).copy()

        d = self._mean.shape[0]
        if self._covariance.shape != (d, d):
            raise ValueError(
                f"initial_covariance must have shape ({d}, {d}), got {self._covariance.shape}"
            )
        if self._process_noise.shape != (d, d):
            raise ValueError(
                f"process_noise_covariance must have shape ({d}, {d}), got {self._process_noise.shape}"
            )

    def predict(self, dt: float) -> None:
        # F is fixed to the identity: the process model is a random walk,
        # not a velocity model, so dt only scales the process noise.
        self._covariance = self._covariance + self._process_noise * dt

    def update(self, observation) -> None:
        z = observation.value
        r = observation.covariance
        identity = np.eye(self._mean.shape[0])

        innovation = z - self._mean
        innovation_covariance = self._covariance + r
        kalman_gain = self._covariance @ np.linalg.inv(innovation_covariance)

        self._mean = self._mean + kalman_gain @ innovation
        self._covariance = (identity - kalman_gain) @ self._covariance

    def incorporate_peer_estimate(self, sender_id: str, mean: np.ndarray, covariance: np.ndarray) -> None:
        raise NotImplementedError(
            "ReferenceKalmanFilter is intentionally local-only. Peer estimates "
            "received from other agents are typically correlated with this "
            "agent's own estimate, through shared prior fusion history, and "
            "naively averaging them would understate the fused uncertainty. "
            "A consistent fusion rule is a literature-dependent decision; see "
            "simulation/estimation/covariance_intersection.py, which is a "
            "documented stub pending the estimator literature review."
        )

    def estimate(self) -> np.ndarray:
        return self._mean.copy()

    def covariance(self) -> np.ndarray:
        return self._covariance.copy()
