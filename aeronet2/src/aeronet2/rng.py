"""Independent random streams.

Every (seed, role, index) triple maps to its own statistically independent
stream via numpy.random.SeedSequence. This fixes the v1 bug where
``seed + 1000 + agent`` made neighbouring seeds share noise streams.
"""
from __future__ import annotations

import numpy as np

ROLES = {"truth": 1, "sensor": 2, "channel": 3, "outage": 4, "policy": 5, "layout": 6}


def rng_for(seed: int, role: str, index: int = 0) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([int(seed), ROLES[role], int(index)]))
