"""Paired statistics. Fails loudly on non-finite data (the v1 helper silently dropped NaNs)."""
from __future__ import annotations

import numpy as np


def _finite(a, name="values"):
    arr = np.asarray(a, dtype=float)
    if not np.isfinite(arr).all():
        raise ValueError(f"non-finite entries in {name}; refusing to drop them silently")
    return arr


def paired_summary(policy, reference, n_boot: int = 10000, seed: int = 0, margin: float | None = None) -> dict:
    """Paired comparison of per-seed metrics (lower is better). d = policy - reference."""
    a, b = _finite(policy, "policy"), _finite(reference, "reference")
    if a.shape != b.shape:
        raise ValueError("paired samples must have equal length")
    d = a - b
    n = len(d)
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    flips = rng.choice([-1.0, 1.0], size=(n_boot, n))
    p = float((np.abs((flips * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).mean())
    sd = d.std(ddof=1)
    out = dict(n=n, mean_diff=float(d.mean()), ci_lo=float(lo), ci_hi=float(hi),
               rel_diff=float(d.mean() / b.mean()), dz=float(d.mean() / sd) if sd > 0 else float("nan"),
               p_signflip=max(p, 1.0 / n_boot))
    if margin is not None:
        out["equivalent_within_margin"] = bool(lo > -margin and hi < margin)
        out["margin"] = margin
    return out


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for k, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - k) * p))
        adj[name] = running
    return adj
