"""Experiment F: accuracy-vs-communication frontier + ablation ladder, nominal vs manoeuvring target."""
import sys, time
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import run_grid, save
from aeronet2.model import Scenario
from aeronet2.stats import paired_summary, holm

NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SEEDS = range(20000, 20000 + NSEED)
POLS = ("none", "periodic", "random", "delta", "innov", "voi_blind", "voi_open", "voi_fb", "voi_psa", "ci_periodic", "broadcast")
SCEN = {
    "nominal": dict(manoeuvre_rate=0.0),
    "manoeuvre": dict(manoeuvre_rate=0.02, manoeuvre_acc=0.5, manoeuvre_len=10),
}
out, t0 = {}, time.time()
for name, kw in SCEN.items():
    out[name] = {}
    for B in (10, 20, 40, 80):
        sc = Scenario(q=0.01, anisotropy=6, budget=B, steps=200, **kw)
        res = run_grid(sc, POLS, SEEDS)
        per = np.array([x.rmse_ss for x in res["periodic"]])
        cell = {}
        pv = {}
        for p in POLS:
            v = np.array([x.rmse_ss for x in res[p]])
            cell[p] = dict(rmse=float(v.mean()), sent=float(np.mean([x.sent_per_agent for x in res[p]])),
                           bytes=float(np.mean([x.bytes_sent for x in res[p]])),
                           delivered=float(np.nanmean([x.delivered_frac for x in res[p]])) if p != "none" else None,
                           nees=float(np.mean([x.nees_ss for x in res[p]])),
                           vs_periodic=paired_summary(v, per, seed=2) if p != "periodic" else None)
            if p not in ("periodic", "none", "broadcast"):
                pv[p] = cell[p]["vs_periodic"]["p_signflip"]
        for p, a in holm(pv).items():
            cell[p]["vs_periodic"]["p_holm"] = a
        out[name][B] = cell
        print("%-9s B=%3d periodic=%.3f psa=%.3f (%+.1f%%) innov=%+.1f%% random=%+.1f%% open=%+.1f%% [%.0fs]" % (
            name, B, cell["periodic"]["rmse"], cell["voi_psa"]["rmse"], 100 * cell["voi_psa"]["vs_periodic"]["rel_diff"],
            100 * cell["innov"]["vs_periodic"]["rel_diff"], 100 * cell["random"]["vs_periodic"]["rel_diff"],
            100 * cell["voi_open"]["vs_periodic"]["rel_diff"], time.time() - t0), flush=True)
save("frontier_ablation.json", dict(seeds=[SEEDS.start, SEEDS.stop], policies=POLS, results=out))
