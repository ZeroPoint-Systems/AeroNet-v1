"""Covariance intersection, a placeholder pending the estimator literature
review.

STATUS: LITERATURE-DEPENDENT

Distributed cooperative localisation has a substantial body of existing
work on this exact problem: naively averaging two agents' estimates, or
naively averaging their covariances, produces a fused result that
understates the true uncertainty whenever the two estimates are
correlated, for example because they were both updated using information
that ultimately traces back to the same earlier measurement. Covariance
intersection, and related consistent fusion rules, exist specifically to
avoid that failure.

This module exists so that the research question of which fusion rule to
use is visible in the code as an open, tracked decision, rather than
silently resolved by whichever rule happened to be easiest to implement.
It is not wired into the experiment runner, and selecting it in a
configuration file is expected to raise NotImplementedError, until
research/literature_review.md and theory/estimator_model.md have
established which formulation to use and why.
"""

from __future__ import annotations

import numpy as np


class CovarianceIntersectionEstimator:
    """Not yet implemented. See the module docstring above."""

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "CovarianceIntersectionEstimator is a documented placeholder. "
            "Its fusion rule is STATUS: LITERATURE-DEPENDENT and has not yet "
            "been chosen. See research/literature_review.md and "
            "theory/estimator_model.md."
        )

    def predict(self, dt: float) -> None:
        raise NotImplementedError

    def update(self, observation) -> None:
        raise NotImplementedError

    def incorporate_peer_estimate(self, sender_id: str, mean: np.ndarray, covariance: np.ndarray) -> None:
        raise NotImplementedError

    def estimate(self) -> np.ndarray:
        raise NotImplementedError

    def covariance(self) -> np.ndarray:
        raise NotImplementedError
