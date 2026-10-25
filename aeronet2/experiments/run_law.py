"""Experiment L: how does the adaptive-communication gain depend on model mismatch?

Pre-registered question (see docs/PREREGISTRATION.md): H2' -- adaptive triggers beat the best periodic
schedule only to the extent the filters' model is inconsistent with reality. We sweep manoeuvre
rate x amplitude, quantify the mismatch with mu = duty * acc^2 (mean squared unmodelled acceleration),
and measure G = relative RMSE reduction of each policy vs periodic at (matched) budget.
"""
import sys, itertools, time
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import run_grid, save
from aeronet2.model import Scenario
from aeronet2.stats import paired_summary

SEEDS = range(10000, 10000 + int(sys.argv[1]) if len(sys.argv) > 1 else 10020)
POLS = ("periodic", "innov", "voi_fb", "voi_psa", "none", "broadcast")
rows = []
t0 = time.time()
for rate, acc in itertools.product([0.0, 0.005, 0.01, 0.02, 0.04], [0.25, 0.5, 1.0]):
    if rate == 0.0 and acc != 0.25:
        continue
    sc = Scenario(q=0.01, anisotropy=6, budget=30, steps=200, manoeuvre_rate=rate, manoeuvre_acc=acc, manoeuvre_len=10)
    duty = rate * sc.manoeuvre_len / (1 + rate * sc.manoeuvre_len)
    mu = duty * acc**2
    res = run_grid(sc, POLS, SEEDS)
    r = {p: np.array([x.rmse_ss for x in res[p]]) for p in POLS}
    row = dict(rate=rate, acc=acc, duty=duty, mu=mu, rmse={p: float(r[p].mean()) for p in POLS},
               sent={p: float(np.mean([x.sent_per_agent for x in res[p]])) for p in POLS})
    for p in ("innov", "voi_fb", "voi_psa"):
        row["vs_periodic_" + p] = paired_summary(r[p], r["periodic"], seed=1, margin=0.01 * r["periodic"].mean())
    row["gap_closed"] = {p: float((r["none"].mean() - r[p].mean()) / (r["none"].mean() - r["broadcast"].mean())) for p in POLS}
    rows.append(row)
    print("rate=%.3f acc=%.2f mu=%.4f  periodic=%.3f psa=%.3f (%+.1f%%) innov=%+.1f%%  [%.0fs]" % (
        rate, acc, mu, r["periodic"].mean(), r["voi_psa"].mean(), 100 * row["vs_periodic_voi_psa"]["rel_diff"],
        100 * row["vs_periodic_innov"]["rel_diff"], time.time() - t0), flush=True)
save("law_manoeuvre_sweep.json", dict(seeds=[SEEDS.start, SEEDS.stop], rows=rows))
