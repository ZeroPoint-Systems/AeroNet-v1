import argparse
import csv
import json
from pathlib import Path
import numpy as np
from .config import ExperimentConfig
from .policies import build_policies
from .simulation import run_trial


def paired_bootstrap_ci(differences, seed=20261024, resamples=10000):
    values = np.asarray(differences, dtype=float)
    if len(values) == 0:
        return [0.0, 0.0]
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(resamples, len(values)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def summarise(rows):
    summary = {}
    for name in sorted({row["policy"] for row in rows}):
        group = [row for row in rows if row["policy"] == name]
        values = np.asarray([row["position_rmse"] for row in group])
        summary[name] = {
            "trials": len(group),
            "position_rmse_mean": float(values.mean()),
            "position_rmse_sd": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
            "messages_sent_mean": float(np.mean([r["messages_sent"] for r in group])),
            "bytes_sent_mean": float(np.mean([r["bytes_sent"] for r in group])),
            "messages_delivered_mean": float(np.mean([r["messages_delivered"] for r in group])),
            "messages_dropped_mean": float(np.mean([r["messages_dropped"] for r in group])),
            "warning_precision_mean": float(np.mean([r["warning_metrics"]["precision"] for r in group])),
            "warning_recall_mean": float(np.mean([r["warning_metrics"]["recall"] for r in group])),
            "warning_false_positive_rate_mean": float(np.mean([r["warning_metrics"]["false_positive_rate"] for r in group])),
        }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run reproducible AeroNet policy comparisons.")
    parser.add_argument("--config", default="configs/default.json")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    if args.seeds < 2:
        parser.error("--seeds must be >= 2 for paired uncertainty estimates")
    config = ExperimentConfig.load(args.config)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    policy_names = [p.name for p in build_policies(config)]
    rows = []
    for idx in range(args.seeds):
        seed = config.seed + idx
        for name in policy_names:
            print(f"seed={seed} policy={name}", flush=True)
            rows.append(run_trial(config, seed, name))
    (out / "trials.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    fields = ["seed", "policy", "position_rmse", "mean_position_error", "messages_sent",
              "bytes_sent", "messages_delivered", "messages_dropped"]
    with (out / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fields})
    summary = summarise(rows)
    # Paired trial-level differences against the no-communication baseline.
    baseline = {r["seed"]: r["position_rmse"] for r in rows if r["policy"] == "none"}
    comparisons = {}
    for name in policy_names:
        if name == "none":
            continue
        by_seed = {r["seed"]: r["position_rmse"] for r in rows if r["policy"] == name}
        seeds = sorted(set(baseline) & set(by_seed))
        diffs = [by_seed[s] - baseline[s] for s in seeds]
        comparisons[name + "_minus_none"] = {
            "mean_paired_rmse_difference": float(np.mean(diffs)),
            "bootstrap_95pct_ci": paired_bootstrap_ci(diffs, seed=config.seed),
            "negative_favours_policy": True,
            "paired_trials": len(diffs),
        }
    report = {"config": config.__dict__, "summary": summary, "paired_comparisons": comparisons}
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
