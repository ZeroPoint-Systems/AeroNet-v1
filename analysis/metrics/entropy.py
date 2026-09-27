"""Gaussian differential entropy.

H(X) = 0.5 * log( (2 * pi * e)^d * det(P) ), computed in nats, for a
d-dimensional Gaussian with covariance P. This is a candidate information
metric, not the chosen primary metric for the information boundary; see
theory/information_boundary.md.
"""

from __future__ import annotations

import math

import numpy as np


def gaussian_entropy(covariance: np.ndarray) -> float:
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError(f"covariance must be square, got shape {covariance.shape}")
    d = covariance.shape[0]
    determinant = np.linalg.det(covariance)
    if determinant <= 0:
        raise ValueError(
            f"covariance must be positive definite to have a well defined entropy, "
            f"got determinant {determinant!r}"
        )
    return 0.5 * (d * math.log(2 * math.pi * math.e) + math.log(determinant))
