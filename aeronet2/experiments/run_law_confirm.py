"""Confirmatory run for the mismatch law: NEW configurations and NEW seeds, predictions frozen from law_fit.json
(which was fitted on the exploratory sweep) BEFORE any of these simulations are run."""
import sys, json, os, itertools, time
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import run_grid, save, RESULTS
from aeronet2.model import Scenario
from aeronet2.stats import paired_summary

fit = json.load(open(os.path.join(RESULTS, "law_fit.json")))
SEEDS = range(30000, 30000 + (int(sys.argv[1]) if len(sys.argv) > 1 else 20))
POLS = ("periodic", "voi_psa")
configs = [(r, a) for r, a in itertools.product([0.003, 0.015, 0.03, 0.08], [0.35, 0.7])]
pred = []
for r, a in configs:                                   # freeze predictions first
    duty = r * 10 / (1 + r * 10)
    mu, nu = duty * a * a, a * a * np.sqrt(duty * (1 - duty))
    pred.append(dict(rate=r, acc=a, mu=mu, nu=nu, pred_mu=fit["mu"]["a"] * mu ** fit["mu"]["b"],
                     pred_nu=fit["nu"]["a"] * nu ** fit["nu"]["b"]))
save("law_confirm_predictions.json", pred)
rows, t0 = [], time.time()
for p in pred:
    sc = Scenario(q=0.01, anisotropy=6, budget=30, steps=200, manoeuvre_rate=p["rate"], manoeuvre_acc=p["acc"], manoeuvre_len=10)
    res = run_grid(sc, POLS, SEEDS)
    v = {k: np.array([x.rmse_ss for x in res[k]]) for k in POLS}
    s = paired_summary(v["voi_psa"], v["periodic"], seed=3)
    rows.append(dict(**p, observed=-s["rel_diff"], ci=[-s["ci_hi"] / v["periodic"].mean(), -s["ci_lo"] / v["periodic"].mean()]))
    print("rate=%.3f acc=%.2f  observed %.1f%% [%.1f,%.1f]  pred(mu)=%.1f%% pred(nu)=%.1f%%  [%.0fs]" % (
        p["rate"], p["acc"], 100 * rows[-1]["observed"], 100 * rows[-1]["ci"][0], 100 * rows[-1]["ci"][1],
        100 * p["pred_mu"], 100 * p["pred_nu"], time.time() - t0), flush=True)
obs = np.array([r["observed"] for r in rows])
summ = []
for k in ("pred_mu", "pred_nu"):
    pr = np.array([r[k] for r in rows])
    mae = float(np.mean(np.abs(pr - obs))); ss = float(np.sum((obs - pr) ** 2)); st = float(np.sum((obs - obs.mean()) ** 2))
    summ.append({"summary": k, "mean_abs_error": mae, "r2_out_of_sample": 1 - ss / st})
    print(k, "MAE=%.2f%% out-of-sample R^2=%.2f" % (100 * mae, 1 - ss / st))
save("law_confirm.json", dict(rows=rows, summary=summ))
