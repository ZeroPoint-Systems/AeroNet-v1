"""Numerically validated covariance-intersection fusion primitives."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def _validated_gaussian(
    mean: ArrayLike,
    covariance: ArrayLike,
    name: str,
) -> tuple[FloatArray, FloatArray]:
    m = np.asarray(mean, dtype=np.float64)
    p = np.asarray(covariance, dtype=np.float64)

    if m.ndim == 2 and 1 in m.shape:
        m = m.reshape(-1)

    if m.ndim != 1 or m.size == 0:
        raise ValueError(f"{name} mean must be a non-empty vector.")

    if p.shape != (m.size, m.size):
        raise ValueError(f"{name} covariance has an incompatible shape.")

    if not np.all(np.isfinite(m)) or not np.all(np.isfinite(p)):
        raise ValueError(f"{name} contains non-finite values.")

    if not np.allclose(p, p.T, rtol=1e-9, atol=1e-12):
        raise ValueError(f"{name} covariance must be symmetric.")

    p = (p + p.T) / 2.0

    try:
        np.linalg.cholesky(p)
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            f"{name} covariance must be positive definite."
        ) from exc

    return m, p


def fuse_gaussians(
    mean_a: ArrayLike,
    covariance_a: ArrayLike,
    mean_b: ArrayLike,
    covariance_b: ArrayLike,
    *,
    weight: float | None = None,
    criterion: Literal["trace", "logdet"] = "trace",
    grid_size: int = 1001,
) -> tuple[FloatArray, FloatArray, float]:
    """Fuse two Gaussian estimates with unknown cross-correlation.

    The returned weight is the contribution assigned to estimate A.
    If weight is omitted, a deterministic grid search minimises either
    the fused covariance trace or its log determinant.

    Returns:
        (fused_mean, fused_covariance, weight_a)
    """
    ma, pa = _validated_gaussian(mean_a, covariance_a, "Estimate A")
    mb, pb = _validated_gaussian(mean_b, covariance_b, "Estimate B")

    if ma.shape != mb.shape:
        raise ValueError("Estimate means must have matching dimensions.")

    if criterion not in ("trace", "logdet"):
        raise ValueError("criterion must be 'trace' or 'logdet'.")

    if weight is not None and not 0.0 <= weight <= 1.0:
        raise ValueError("weight must lie between 0 and 1.")

    if not isinstance(grid_size, int) or grid_size < 2:
        raise ValueError("grid_size must be an integer of at least 2.")

    info_a = np.linalg.solve(pa, np.eye(pa.shape[0]))
    info_b = np.linalg.solve(pb, np.eye(pb.shape[0]))
    info_a = (info_a + info_a.T) / 2.0
    info_b = (info_b + info_b.T) / 2.0

    def evaluate(w: float) -> tuple[FloatArray, FloatArray, float]:
        information = w * info_a + (1.0 - w) * info_b
        information = (information + information.T) / 2.0

        fused_cov = np.linalg.solve(
            information, np.eye(information.shape[0])
        )
        fused_cov = (fused_cov + fused_cov.T) / 2.0

        fused_mean = fused_cov @ (
            w * (info_a @ ma) + (1.0 - w) * (info_b @ mb)
        )

        if criterion == "trace":
            score = float(np.trace(fused_cov))
        else:
            sign, logdet = np.linalg.slogdet(fused_cov)
            if sign <= 0:
                raise ValueError("Fused covariance is not positive definite.")
            score = float(logdet)

        return fused_mean, fused_cov, score

    if weight is not None:
        fused_mean, fused_cov, _ = evaluate(float(weight))
        return fused_mean, fused_cov, float(weight)

    best_weight = 0.0
    best_result = evaluate(best_weight)

    for candidate in np.linspace(0.0, 1.0, grid_size)[1:]:
        result = evaluate(float(candidate))
        if result[2] < best_result[2]:
            best_weight = float(candidate)
            best_result = result

    return best_result[0], best_result[1], best_weight
