"""Sensing-and-communication allocation experiments.

    python experiments/run_cdia.py run main        # validation seeds 2000-2029, budgets 5/10/20
    python experiments/run_cdia.py run heldout     # confirmation seeds 3000-3019, changed conditions
    python experiments/run_cdia.py analyse main|heldout

Scenario fixed from the pilot on development seeds 1000-1009. Primary outcome: team decision error rate
(steady state), paired by seed. Raw per-trial records are written once and never overwritten.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
from aeronet2.cdia.sim import Decision, run_trial  # noqa: E402
from aeronet2.model import Scenario  # noqa: E402
from aeronet2.stats import holm, paired_summary  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "results", "cdia")
BASE = dict(q=1e-4, prior_vel_var=0.04, prior_pos_var=1.0, sigma=2.5, sensor_spread=0.7, anisotropy=4, steps=200)
DEC = Decision(angle=0.0, tau=0.0)
KAPPA, SENSE_COST = 4.0, 1.0

BUDGET_POLICIES = ("periodic_comm", "periodic_split", "innov_comm", "trace_comm", "trace_joint", "cdia_comm", "cdia")
FREE_POLICIES = ("none", "broadcast")

PLANS = {
    "main": dict(seeds=range(2000, 2030),
                 conditions={"base": {}},
                 budgets=(5, 10, 20), policies=BUDGET_POLICIES),
    "heldout": dict(seeds=range(3000, 3020),
                    conditions={
                        "agents10": dict(n_agents=10),
                        "complete6": dict(topology="complete"),
                        "line6": dict(topology="line"),
                        "lossy_outage": dict(loss=0.3, outage_rate=0.01),
                        "manoeuvre": dict(manoeuvre_rate=0.02, manoeuvre_acc=0.5, manoeuvre_len=10),
                        "costly_sensing": dict(),
                    },
                    budgets=(10,), policies=("periodic_split", "innov_comm", "trace_joint", "cdia_comm", "cdia")),
}
CONTRASTS = (("cdia", "trace_joint"), ("cdia", "periodic_split"), ("cdia", "innov_comm"))


def _job(args):
    cond, kw, budget, policy, seed = args
    sc = Scenario(**{**BASE, **kw}, budget=budget)
    kappa, cost = (2.0, 2.0) if cond == "costly_sensing" else (KAPPA, SENSE_COST)
    r = run_trial(sc, policy, seed, DEC, kappa=kappa, sense_cost=cost)
    return dict(condition=cond, budget=budget, kappa=kappa, sense_cost=cost, **asdict(r))


def revision() -> dict:
    def git(*a):
        return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout.strip()
    return dict(commit=git("rev-parse", "HEAD"), dirty=bool(git("status", "--porcelain")))


def run(plan_name: str) -> None:
    plan = PLANS[plan_name]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"raw_{plan_name}.jsonl")
    jobs = []
    for cond, kw in plan["conditions"].items():
        for seed in plan["seeds"]:
            for p in FREE_POLICIES:
                jobs.append((cond, kw, plan["budgets"][0], p, seed))
            for b in plan["budgets"]:
                for p in plan["policies"]:
                    jobs.append((cond, kw, b, p, seed))
    header = dict(record="header", plan=plan_name, base=BASE, decision=asdict(DEC), kappa=KAPPA, sense_cost=SENSE_COST,
                  seeds=[plan["seeds"].start, plan["seeds"].stop], conditions=plan["conditions"],
                  budgets=plan["budgets"], policies=plan["policies"], revision=revision(), jobs=len(jobs),
                  versions=dict(python=sys.version.split()[0], numpy=np.__version__))
    with open(path, "x") as f, Pool(2) as pool:
        f.write(json.dumps(header) + "\n")
        for k, rec in enumerate(pool.imap(_job, jobs, chunksize=4)):
            f.write(json.dumps(dict(record="trial", **rec)) + "\n")
            if k % 100 == 0:
                print(f"{k}/{len(jobs)}", flush=True)
    print("wrote", path)


def analyse(plan_name: str) -> None:
    path = os.path.join(OUT, f"raw_{plan_name}.jsonl")
    rows = [json.loads(line) for line in open(path)]
    header, trials = rows[0], [r for r in rows[1:] if r["record"] == "trial"]
    if len(trials) != header["jobs"]:
        raise SystemExit(f"incomplete raw file: {len(trials)} of {header['jobs']} trials")
    for r in trials:
        for k in ("decision_error", "rmse_ss"):
            if not np.isfinite(r[k]):
                raise SystemExit("non-finite value in raw record")
    key = lambda r: (r["condition"], r["budget"] if r["policy"] not in FREE_POLICIES else None, r["policy"])
    cells: dict = {}
    for r in trials:
        cells.setdefault(key(r), {})[r["seed"]] = r
    out, tests = {}, {}
    for (cond, budget, pol), by_seed in sorted(cells.items(), key=lambda kv: str(kv[0])):
        seeds = sorted(by_seed)
        v = lambda f: np.array([by_seed[s][f] for s in seeds])
        out[f"{cond}|{budget}|{pol}"] = dict(
            n=len(seeds), decision_error=float(v("decision_error").mean()), rmse=float(v("rmse_ss").mean()),
            units=float(v("units_per_agent").mean()), sent=float(v("sent_per_agent").mean()),
            sensed=float(v("sensed_per_agent").mean()), bytes=float(v("bytes_sent").mean()),
            policy_ms_per_decision=float(1e3 * v("policy_seconds").sum() / v("decisions_evaluated").sum()))
    for cond in header["conditions"]:
        for b in header["budgets"]:
            for a, ref in CONTRASTS:
                ca, cr = cells.get((cond, b, a)), cells.get((cond, b, ref))
                if ca is None or cr is None:
                    continue
                seeds = sorted(set(ca) & set(cr))
                va = np.array([ca[s]["decision_error"] for s in seeds])
                vr = np.array([cr[s]["decision_error"] for s in seeds])
                s = paired_summary(va, vr, seed=7)
                s["ref_mean"] = float(vr.mean())
                s["units_a"] = out[f"{cond}|{b}|{a}"]["units"]
                s["units_ref"] = out[f"{cond}|{b}|{ref}"]["units"]
                tests[f"{cond}|{b}|{a}-{ref}"] = s
    adj = holm({k: v["p_signflip"] for k, v in tests.items()})
    for k in tests:
        tests[k]["p_holm"] = adj[k]
    res = os.path.join(OUT, f"summary_{plan_name}.json")
    with open(res, "w") as f:
        json.dump(dict(header=header, cells=out, contrasts=tests), f, indent=1)
    print(f"{'cell':44s} {'dec.err':>8s} {'rmse':>6s} {'units':>6s} {'sent':>5s} {'sens':>5s} {'ms/dec':>7s}")
    for k, v in out.items():
        print(f"{k:44s} {100*v['decision_error']:7.2f}% {v['rmse']:6.3f} {v['units']:6.1f} {v['sent']:5.1f} {v['sensed']:5.1f} {v['policy_ms_per_decision']:7.3f}")
    print("\npaired decision-error contrasts (cdia minus reference; negative favours cdia)")
    for k, v in tests.items():
        print(f"{k:50s} {100*v['mean_diff']:+.3f} pts [{100*v['ci_lo']:+.3f},{100*v['ci_hi']:+.3f}] rel {100*v['rel_diff']:+.1f}% "
              f"dz={v['dz']:+.2f} p_holm={v['p_holm']:.4f} units {v['units_a']:.1f} vs {v['units_ref']:.1f}")


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    run(name) if cmd == "run" else analyse(name)
