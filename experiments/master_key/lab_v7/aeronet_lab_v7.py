from __future__ import annotations

import csv
import importlib.util
import inspect
import json
import math
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments" / "master_key" / "lab_v5" / "aeronet_lab_v5.py"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_DIR = Path(__file__).resolve().parent / "runs" / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=False)

# Pilot-derived operational threshold. Freeze this before examining Lab v7.
# It is a provisional research criterion, not a universal stability definition.
RMSE_LIMIT = 1.75
SEEDS = list(range(20261120, 20261130))
SENSING_FACTORS = [0.75, 1.0, 1.35]
PACKET_LOSS_LEVELS = [0.0, 0.10, 0.25]
REACTIVE_THRESHOLDS = [(2.0, 3.0), (3.0, 5.0), (4.0, 7.0)]
PREDICTIVE_THRESHOLDS = [0.8, 1.0, 1.15, 1.5, 2.0]

def load_simulator():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing simulator: {SOURCE}")
    spec = importlib.util.spec_from_file_location("aeronet_lab_v5_runtime", SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "run_trial") or not hasattr(module, "should_send"):
        raise RuntimeError("Lab v5 must expose run_trial and should_send.")
    return module

lab = load_simulator()
original_should_send = lab.should_send
original_packet_loss = getattr(lab, "PACKET_LOSS", None)
original_sensor_scales = getattr(lab, "SENSOR_SCALES", None)

def install_policy(policy, covariance_threshold=3.0,
                   nis_threshold=5.0, risk_threshold=1.15):
    def policy_rule(name, agent, t):
        if name == "none":
            return False
        if name == "periodic":
            return t % lab.WINDOW == 0

        window = t // lab.WINDOW
        if getattr(agent, "last_sent_window", None) == window:
            return False

        if name == "reactive":
            return (
                float(np.trace(agent.P[:2, :2])) > covariance_threshold
                or float(getattr(agent, "nis", 0.0)) > nis_threshold
            )
        if name == "predictive":
            return float(getattr(agent, "risk", 0.0)) > risk_threshold
        raise ValueError(f"Unknown policy: {name}")

    lab.should_send = policy_rule

def set_condition(sensing_factor, packet_loss):
    if original_packet_loss is not None:
        lab.PACKET_LOSS = float(packet_loss)

    # Scale the simulator's existing heterogeneous sensor settings.
    # The baseline list is restored before each condition to prevent drift.
    if original_sensor_scales is not None:
        lab.SENSOR_SCALES = [
            float(x) * float(sensing_factor) for x in original_sensor_scales
        ]

def invoke_trial(seed, policy):
    signature = inspect.signature(lab.run_trial)
    params = signature.parameters
    kwargs = {}
    for name in params:
        lower = name.lower()
        if lower in {"seed", "random_seed", "rng_seed"}:
            kwargs[name] = int(seed)
        elif lower in {"policy", "strategy", "communication_policy"}:
            kwargs[name] = policy

    required = [
        p for p in params.values()
        if p.default is inspect.Parameter.empty
        and p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    ]
    missing = [p.name for p in required if p.name not in kwargs]
    if missing:
        raise RuntimeError(
            f"Cannot safely call run_trial{signature}; unresolved parameters: {missing}"
        )
    return lab.run_trial(**kwargs)

def find_metric(obj, names):
    if isinstance(obj, dict):
        lowered = {str(k).lower(): v for k, v in obj.items()}
        for name in names:
            if name.lower() in lowered:
                try:
                    value = float(lowered[name.lower()])
                    if math.isfinite(value):
                        return value
                except (TypeError, ValueError):
                    pass
        for value in obj.values():
            found = find_metric(value, names)
            if found is not None:
                return found
    elif hasattr(obj, "__dict__"):
        return find_metric(vars(obj), names)
    return None

def normalise_result(result, seed, condition, policy, thresholds):
    rmse = find_metric(result, ["rmse", "final_rmse", "position_rmse", "mean_rmse"])
    broadcasts = find_metric(result, ["broadcasts", "attempted_broadcasts", "messages", "messages_sent",
                                      "total_broadcasts", "send_count"])
    delivered = find_metric(result, ["delivered", "delivered_messages",
                                     "delivered_links", "messages_delivered"])
    if rmse is None or broadcasts is None:
        raise RuntimeError(
            "run_trial returned an unrecognised result schema. "
            f"Return type={type(result).__name__}; "
            f"keys={list(result.keys()) if isinstance(result, dict) else 'not a dict'}. "
            "No results were silently discarded."
        )
    return {
        "seed": int(seed),
        "sensing_factor": float(condition["sensing_factor"]),
        "packet_loss": float(condition["packet_loss"]),
        "policy": policy,
        "covariance_threshold": thresholds.get("covariance"),
        "nis_threshold": thresholds.get("nis"),
        "risk_threshold": thresholds.get("risk"),
        "rmse": float(rmse),
        "rmse_limit": RMSE_LIMIT,
        "within_limit": bool(rmse <= RMSE_LIMIT),
        "broadcasts": float(broadcasts),
        "delivered": delivered,
    }

def bootstrap_mean_ci(values, seed=90210, reps=5000):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return [None, None]
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(reps, len(values)), replace=True).mean(axis=1)
    return [
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    ]

def summarise(rows):
    groups = {}
    for row in rows:
        key = (
            row["sensing_factor"], row["packet_loss"], row["policy"],
            row["covariance_threshold"], row["nis_threshold"], row["risk_threshold"]
        )
        groups.setdefault(key, []).append(row)

    summaries = []
    for key, group in groups.items():
        errors = np.asarray([r["rmse"] for r in group], dtype=float)
        messages = np.asarray([r["broadcasts"] for r in group], dtype=float)
        summaries.append({
            "sensing_factor": key[0],
            "packet_loss": key[1],
            "policy": key[2],
            "covariance_threshold": key[3],
            "nis_threshold": key[4],
            "risk_threshold": key[5],
            "n": len(group),
            "mean_rmse": float(errors.mean()),
            "sd_rmse": float(errors.std(ddof=1)) if len(errors) > 1 else 0.0,
            "rmse_ci95_bootstrap": bootstrap_mean_ci(errors),
            "mean_broadcasts": float(messages.mean()),
            "mean_delivered": (
                float(np.mean([r["delivered"] for r in group
                               if r["delivered"] is not None]))
                if any(r["delivered"] is not None for r in group) else None
            ),
            "success_fraction": float(np.mean(errors <= RMSE_LIMIT)),
        })
    return summaries

def estimate_boundary(summaries):
    # For each sensing/network condition, find the lowest observed mean
    # broadcast count among policies meeting the predeclared RMSE criterion.
    conditions = sorted({
        (s["sensing_factor"], s["packet_loss"]) for s in summaries
    })
    output = []
    for sensing, loss in conditions:
        group = [
            s for s in summaries
            if s["sensing_factor"] == sensing and s["packet_loss"] == loss
        ]
        eligible = [s for s in group if s["mean_rmse"] <= RMSE_LIMIT]
        eligible.sort(key=lambda s: s["mean_broadcasts"])
        output.append({
            "sensing_factor": sensing,
            "packet_loss": loss,
            "rmse_limit": RMSE_LIMIT,
            "boundary_observed": bool(eligible),
            "minimum_observed_mean_broadcasts": (
                eligible[0]["mean_broadcasts"] if eligible else None
            ),
            "selected_policy": eligible[0]["policy"] if eligible else None,
            "selected_mean_rmse": eligible[0]["mean_rmse"] if eligible else None,
            "selected_success_fraction": eligible[0]["success_fraction"] if eligible else None,
            "interpretation": (
                "lowest tested communication cost meeting the criterion"
                if eligible else
                "no tested policy met the criterion"
            ),
        })
    return output

def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def make_plots(summaries, boundaries):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for sensing in SENSING_FACTORS:
        subset = [s for s in summaries if s["sensing_factor"] == sensing]
        fig, ax = plt.subplots()
        for loss in PACKET_LOSS_LEVELS:
            group = [s for s in subset if s["packet_loss"] == loss]
            group.sort(key=lambda s: s["mean_broadcasts"])
            if group:
                ax.scatter(
                    [s["mean_broadcasts"] for s in group],
                    [s["mean_rmse"] for s in group],
                    label=f"packet loss={loss:.2f}",
                    alpha=0.8,
                )
        ax.axhline(RMSE_LIMIT, linestyle="--", label=f"RMSE limit={RMSE_LIMIT}")
        ax.set_xlabel("Mean broadcasts per trial")
        ax.set_ylabel("Mean RMSE")
        ax.set_title(f"Communication-accuracy frontier, sensing factor={sensing}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(RUN_DIR / f"frontier_sensing_{sensing:.2f}.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots()
    for sensing in SENSING_FACTORS:
        group = [b for b in boundaries if b["sensing_factor"] == sensing
                 and b["minimum_observed_mean_broadcasts"] is not None]
        group.sort(key=lambda b: b["packet_loss"])
        if group:
            ax.plot(
                [b["packet_loss"] for b in group],
                [b["minimum_observed_mean_broadcasts"] for b in group],
                marker="o", label=f"sensing factor={sensing:.2f}"
            )
    ax.set_xlabel("Packet loss probability")
    ax.set_ylabel("Minimum observed mean broadcasts meeting RMSE limit")
    ax.set_title("Estimated communication boundary")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RUN_DIR / "estimated_boundary.png", dpi=180)
    plt.close(fig)

def main():
    policies = [("none", {}), ("periodic", {})]
    policies += [
        ("reactive", {"covariance": cov, "nis": nis})
        for cov, nis in REACTIVE_THRESHOLDS
    ]
    policies += [
        ("predictive", {"risk": risk})
        for risk in PREDICTIVE_THRESHOLDS
    ]

    rows = []
    total = len(SEEDS) * len(SENSING_FACTORS) * len(PACKET_LOSS_LEVELS) * len(policies)
    count = 0
    print(f"Lab v7 run: {RUN_ID}")
    print(f"Trials planned: {total}")
    print(f"RMSE criterion: {RMSE_LIMIT}")
    print("No source files from earlier labs will be modified.")

    try:
        for sensing in SENSING_FACTORS:
            for loss in PACKET_LOSS_LEVELS:
                condition = {"sensing_factor": sensing, "packet_loss": loss}
                set_condition(sensing, loss)
                for policy, thresholds in policies:
                    install_policy(
                        policy,
                        covariance_threshold=thresholds.get("covariance", 3.0),
                        nis_threshold=thresholds.get("nis", 5.0),
                        risk_threshold=thresholds.get("risk", 1.15),
                    )
                    for seed in SEEDS:
                        # Re-seed global generators as well as the trial seed,
                        # so condition order does not determine random streams.
                        np.random.seed(seed)
                        result = invoke_trial(seed, policy)
                        rows.append(normalise_result(
                            result, seed, condition, policy, thresholds
                        ))
                        count += 1
                        if count % 50 == 0 or count == total:
                            print(f"Completed {count}/{total}")
    except Exception:
        (RUN_DIR / "failure_traceback.txt").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        raise
    finally:
        lab.should_send = original_should_send
        if original_packet_loss is not None:
            lab.PACKET_LOSS = original_packet_loss
        if original_sensor_scales is not None:
            lab.SENSOR_SCALES = original_sensor_scales

    summaries = summarise(rows)
    boundaries = estimate_boundary(summaries)
    write_csv(RUN_DIR / "trial_results.csv", rows)
    write_csv(RUN_DIR / "policy_summary.csv", summaries)
    write_csv(RUN_DIR / "boundary_estimates.csv", boundaries)
    (RUN_DIR / "metadata.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "source": str(SOURCE.relative_to(ROOT)),
        "seeds": SEEDS,
        "sensing_factors": SENSING_FACTORS,
        "packet_loss_levels": PACKET_LOSS_LEVELS,
        "reactive_thresholds": REACTIVE_THRESHOLDS,
        "predictive_thresholds": PREDICTIVE_THRESHOLDS,
        "rmse_limit": RMSE_LIMIT,
        "trial_count": len(rows),
        "status": "exploratory; selected boundary requires independent confirmation",
    }, indent=2), encoding="utf-8")

    make_plots(summaries, boundaries)
    print("\nBOUNDARY ESTIMATES")
    for row in boundaries:
        print(json.dumps(row, sort_keys=True))
    print(f"\nOutputs: {RUN_DIR}")
    print("Files: trial_results.csv, policy_summary.csv, boundary_estimates.csv,")
    print("       metadata.json, frontier_sensing_*.png, estimated_boundary.png")

if __name__ == "__main__":
    main()

