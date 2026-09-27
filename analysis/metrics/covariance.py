"""Covariance summary metrics.

Candidate scalar summaries of an estimate's covariance matrix, useful for
tracking uncertainty over time without carrying the full matrix through
every downstream calculation.
"""

from __future__ import annotations

import numpy as np


def covariance_trace(covariance: np.ndarray) -> float:
    """tr(P), the sum of the marginal variances."""
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError(f"covariance must be square, got shape {covariance.shape}")
    return float(np.trace(covariance))


def covariance_determinant(covariance: np.ndarray) -> float:
    """det(P), proportional to the volume of the uncertainty ellipsoid."""
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError(f"covariance must be square, got shape {covariance.shape}")
    return float(np.linalg.det(covariance))
