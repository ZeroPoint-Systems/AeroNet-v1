"""Noise models for sensing.

Every stochastic component in the simulator receives an explicit,
caller supplied random number generator. No module in this package ever
calls the global NumPy random state. This is what makes an experiment
exactly reproducible from its recorded seed, and what makes the
deterministic seed test in tests/reproducibility meaningful.
"""

from __future__ import annotations

import numpy as np


class GaussianNoise:
    """Zero mean multivariate Gaussian noise with a fixed covariance.

    Parameters
    ----------
    covariance:
        The noise covariance matrix, R. Must be square and symmetric.
    rng:
        An explicit NumPy random number generator. Never created internally,
        always passed in by the caller, so that a single experiment's random
        stream is fully determined by the seed recorded in its manifest.
    """

    def __init__(self, covariance: np.ndarray, rng: np.random.Generator) -> None:
        covariance = np.asarray(covariance, dtype=float)
        if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
            raise ValueError(f"covariance must be square, got shape {covariance.shape}")
        if not np.allclose(covariance, covariance.T):
            raise ValueError("covariance must be symmetric")
        self.covariance = covariance
        self._rng = rng

    def sample(self) -> np.ndarray:
        """Draw a single noise vector v ~ N(0, R)."""
        dimension = self.covariance.shape[0]
        return self._rng.multivariate_normal(mean=np.zeros(dimension), cov=self.covariance)
