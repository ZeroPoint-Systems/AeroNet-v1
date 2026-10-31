"""Headroom diagnostic: how much decision error can any budgeted allocation remove in the main scenario?

Compares periodic communication, hindsight oracles (labelled references) and the two free references on the
main-experiment seeds. Writes one raw record per trial.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
sys.path.insert(0, HERE)
from run_cdia import BASE, DEC, OUT  # noqa: E402
from aeronet2.cdia.sim import run_trial  # noqa: E402
from aeronet2.model import Scenario  # noqa: E402
from dataclasses import asdict  # noqa: E402

os.makedirs(OUT, exist_ok=True)
rows = []
for seed in range(2000, 2030):
    for B in (5, 20, 60):
        for p in ("periodic_comm", "oracle_send", "oracle_sense"):
            rows.append(dict(budget=B, **asdict(run_trial(Scenario(**BASE, budget=B), p, seed, DEC))))
    for p in ("none", "broadcast"):
        rows.append(dict(budget=0, **asdict(run_trial(Scenario(**BASE, budget=20), p, seed, DEC))))
with open(os.path.join(OUT, "raw_headroom.jsonl"), "x") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
for key in sorted({(r["policy"], r["budget"]) for r in rows}):
    v = [r["decision_error"] for r in rows if (r["policy"], r["budget"]) == key]
    print("%-14s B=%-3d error %.2f%% (se %.2f) units %.1f" % (key[0], key[1], 100 * np.mean(v), 100 * np.std(v, ddof=1) / np.sqrt(len(v)),
          np.mean([r["units_per_agent"] for r in rows if (r["policy"], r["budget"]) == key])))
