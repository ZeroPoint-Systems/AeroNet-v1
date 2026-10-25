from __future__ import annotations
import json, os, time
import numpy as np
from aeronet2.model import Scenario, simulate_measurements, simulate_truth
from aeronet2.sim import run_trial, centralised_rmse

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def run_grid(sc: Scenario, policies, seeds):
    """Return {policy: [TrialResult...]} using common random numbers across policies."""
    out = {p: [] for p in policies}
    for s in seeds:
        truth = simulate_truth(sc, s)
        Z = simulate_measurements(sc, truth, s)
        for p in policies:
            out[p].append(run_trial(sc, p, s, truth=truth, Z=Z))
    return out


def save(name: str, obj) -> str:
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path
