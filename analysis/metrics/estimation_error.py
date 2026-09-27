"""Estimation error metrics.

These are candidate metrics, useful for validating that the simulator and
estimator behave sensibly. None of them is yet the primary information
metric referred to in theory/information_boundary.md, and none of them
should be read as a pre-chosen definition of the critical boundary; that
choice is made separately, and later, in analysis/boundary_estimation.

Every function here is pure: it takes plain arrays or numbers in, and
returns a plain number out, with no side effects and no access to any
simulation object.
"""

from __future__ import annotations

import math

import numpy as np


def position_error(estimate: np.ndarray, truth: np.ndarray) -> float:
    """e_t = || x_hat_t - x_t ||, the Euclidean norm of the estimate error."""
    estimate = np.asarray(estimate, dtype=float)
    truth = np.asarray(truth, dtype=float)
    if estimate.shape != truth.shape:
        raise ValueError(f"estimate and truth must have the same shape, got {estimate.shape} and {truth.shape}")
    return float(np.linalg.norm(estimate - truth))


def squared_error(estimate: np.ndarray, truth: np.ndarray) -> float:
    """e_t^2, the squared Euclidean norm of the estimate error."""
    return position_error(estimate, truth) ** 2


def rmse(errors: "list[float]") -> float:
    """RMSE = sqrt( (1/T) * sum(e_t^2) ), given a sequence of raw position
    errors e_t (not pre-squared).
    """
    if len(errors) == 0:
        raise ValueError("rmse requires at least one error value")
    squared = [e * e for e in errors]
    mean_squared = sum(squared) / len(squared)
    return math.sqrt(mean_squared)
