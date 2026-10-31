"""Decision-theoretic value of an additional measurement.

Team decision: each agent acts on the sign of c.x - tau, where x is the position and c a unit vector.
For a Gaussian belief N(m, s2) of u = c.x the Bayes error of that decision is Phi(-|m - tau| / s).

Adding one position measurement with covariance R to a belief with covariance P changes the belief of u
in two ways: the variance falls from s2 to s2 - v, with v = c'P H'(HPH' + R)^-1 H P c, and the posterior mean
moves by a zero-mean Gaussian step of variance v (preposterior distribution). The expected Bayes error
after the measurement is therefore

    E_xi Phi(-|d + sqrt(v) xi| / sqrt(s2 - v)),   d = m - tau,  xi ~ N(0, 1),

and the counterfactual value is the reduction in expected error. The integral is evaluated on a fixed
trapezoidal grid so that the Python and C++ implementations agree to rounding error.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

GRID_N = 4001
GRID_HALF_WIDTH = 9.0
_XI = np.linspace(-GRID_HALF_WIDTH, GRID_HALF_WIDTH, GRID_N)
_H = _XI[1] - _XI[0]
_W = np.exp(-0.5 * _XI**2) / np.sqrt(2.0 * np.pi) * _H
_W[0] *= 0.5
_W[-1] *= 0.5
_MIN_VAR = 1e-12


def bayes_error(d: float, s2: float) -> float:
    """Probability that the sign decision is wrong under belief N(tau + d, s2)."""
    return float(ndtr(-abs(d) / np.sqrt(max(s2, _MIN_VAR))))


def info_variance(P: np.ndarray, R: np.ndarray, c: np.ndarray) -> float:
    """Variance v of the posterior-mean step of u = c.x caused by one position measurement."""
    M = P[:2, :]                      # H P
    S = P[:2, :2] + R
    g = M @ c                         # H P c
    return float(g @ np.linalg.solve(S, g))


def decision_value(d: float, s2: float, v: float) -> float:
    """Expected reduction in Bayes decision error from a measurement with step variance v."""
    v = min(max(v, 0.0), s2 - _MIN_VAR)
    if v <= 0.0:
        return 0.0
    sp = np.sqrt(s2 - v)
    after = float(np.dot(_W, ndtr(-np.abs(d + np.sqrt(v) * _XI) / sp)))
    return bayes_error(d, s2) - after


def measurement_value(P: np.ndarray, R: np.ndarray, c4: np.ndarray, d: float) -> float:
    """Decision value of one position measurement (covariance R) for a receiver with covariance P and margin d."""
    s2 = float(c4 @ P @ c4)
    return decision_value(d, s2, info_variance(P, R, c4))


def age_inflated_noise(R: np.ndarray, F: np.ndarray, Q: np.ndarray, delay: int) -> np.ndarray:
    """Measurement covariance after propagating the target `delay` steps: R + position block of sum F^k Q F^k'."""
    acc = np.zeros((4, 4))
    Fk = np.eye(4)
    for _ in range(delay):
        acc += Fk @ Q @ Fk.T
        Fk = F @ Fk
    return R + acc[:2, :2]
