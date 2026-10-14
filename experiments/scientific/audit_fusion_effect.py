from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "experiments" / "scientific_campaign" / "mechanism_audit"


def valid_config(path: Path) -> bool:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return (
            isinstance(data, dict)
            and all(key in data for key in (
                "experiment", "simulation", "target", "swarm",
                "sensing", "communication", "estimation"
            ))
            and isinstance(data["communication"], dict)
        )
    except Exception:
        return False


def find_config(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).resolve()
        if not path.is_file() or not valid_config(path):
            raise SystemExit(f"Invalid experiment configuration: {path}")
        return path

    excluded = {"scientific_campaign", "raw", "runs", "__pycache__"}
    candidates = [
        path for path in (ROOT / "experiments").rglob("*.yaml")
        if not any(part in excluded for part in path.parts)
        and valid_config(path)
    ]
    candidates += [
        path for path in (ROOT / "experiments").rglob("*.yml")
        if not any(part in excluded for part in path.parts)
        and valid_config(path)
    ]
    candidates = sorted(set(candidates))

    preferred = [
        path for path in candidates
        if "pilot_001" in path.stem.lower()
    ]
    if len(preferred) == 1:
        return preferred[0]
    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise SystemExit(
            "No suitable YAML configuration found under experiments/. "
            "Pass the base configuration explicitly with --config."
        )

    listing = "\n".join(f"  {path.relative_to(ROOT)}" for path in candidates)
    raise SystemExit(
        "Multiple candidate configurations found. Re-run with "
        "--config followed by the intended YAML path:\n" + listing
    )


def find_output(root: Path) -> Path:
    matches = list(root.rglob("metrics.csv"))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one metrics.csv under {root}, found {len(matches)}. "
            "Inspect the run output before continuing."
        )
    return matches[0].parent


def read_metrics(path: Path) -> dict:
    file = path / "metrics.csv"
    with file.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    values = [
        float(row["rmse"])
        for row in rows
        if row.get("rmse") not in (None, "")
        and math.isfinite(float(row["rmse"]))
    ]
    if not values:
        raise RuntimeError(f"No valid RMSE values found in {file}")

    return {
        "metrics_path": str(file.relative_to(ROOT)),
        "agents_or_rows": len(values),
        "mean_agent_rmse": sum(values) / len(values),
        "agent_rmse": rows,
    }


def read_trajectory(path: Path) -> dict:
    file = path / "trajectory.csv"
    if not file.exists():
        return {"available": False, "rows": 0, "values": {}}

    values = {}
    with file.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            key = (row.get("step"), row.get("agent_id"))
            try:
                values[key] = (
                    float(row["estimate_x"]),
                    float(row["estimate_y"]),
                )
            except (KeyError, TypeError, ValueError):
                continue

    return {
        "available": True,
        "rows": len(values),
        "values": values,
    }


def trajectory_difference(first: dict, second: dict) -> dict:
    a, b = first["values"], second["values"]
    shared = set(a) & set(b)
    if not shared:
        return {
            "comparable_rows": 0,
            "changed_rows": None,
            "changed_fraction": None,
        }

    changed = sum(
        not (
            math.isclose(a[key][0], b[key][0], rel_tol=0, abs_tol=1e-12)
            and math.isclose(a[key][1], b[key][1], rel_tol=0, abs_tol=1e-12)
        )
        for key in shared
    )
    return {
        "comparable_rows": len(shared),
        "changed_rows": changed,
        "changed_fraction": changed / len(shared),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to the base YAML configuration")
    args = parser.parse_args()

    config_path = find_config(args.config)
    base = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    print(f"Repository: {ROOT}")
    print(f"Base configuration: {config_path.relative_to(ROOT)}")
    print(f"Audit output: {AUDIT.relative_to(ROOT)}")

    AUDIT.mkdir(parents=True, exist_ok=True)
    config_dir = AUDIT / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)

    conditions = [
        ("reference_no_fusion", "reference_kalman", False, 0.0),
        ("ci_no_fusion", "covariance_intersection", False, 0.0),
        ("ci_clean", "covariance_intersection", True, 0.0),
        ("ci_loss_50", "covariance_intersection", True, 0.5),
    ]

    sys.path.insert(0, str(ROOT))
    from experiments.runners.run_experiment import run

    results = {}

    for name, method, fusion, loss in conditions:
        config = json.loads(json.dumps(base))
        config.setdefault("experiment", {})
        config["experiment"]["id"] = f"audit_{name}"
        config["experiment"]["seed"] = 20261013

        config.setdefault("estimation", {})
        config["estimation"]["method"] = method

        communication = config.setdefault("communication", {})
        communication["enable_fusion"] = fusion
        communication["packet_loss_probability"] = loss

        config_file = config_dir / f"{name}.yaml"
        config_file.write_text(
            yaml.safe_dump(config, sort_keys=False),
            encoding="utf-8",
        )

        output_root = AUDIT / "runs" / name
        output_root.mkdir(parents=True, exist_ok=True)

        print(f"\nRunning {name}: method={method}, fusion={fusion}, packet loss={loss:.0%}")
        run(config_file, output_root=output_root)

        result_dir = find_output(output_root)
        results[name] = {
            "estimation_method": method,
            "fusion_enabled": fusion,
            "packet_loss_probability": loss,
            "result_directory": str(result_dir.relative_to(ROOT)),
            **read_metrics(result_dir),
            "trajectory": read_trajectory(result_dir),
        }
        results[name]["trajectory"].pop("values", None)
        print(
            f"  Mean per-agent RMSE: "
            f"{results[name]['mean_agent_rmse']:.8f}"
        )

    trajectory_data = {}
    for name, _, _, _ in conditions:
        result_dir = Path(results[name]["result_directory"])
        if not result_dir.is_absolute():
            result_dir = ROOT / result_dir
        trajectory_data[name] = read_trajectory(result_dir)

    comparisons = {
        "covariance_intersection_fusion_vs_no_fusion": trajectory_difference(
            trajectory_data["ci_no_fusion"],
            trajectory_data["ci_clean"],
        ),
        "packet_loss_effect_with_fusion": trajectory_difference(
            trajectory_data["ci_clean"],
            trajectory_data["ci_loss_50"],
        ),
    }

    report = {
        "purpose": "Initial causal mechanism audit, not a novelty test",
        "base_configuration": str(config_path.relative_to(ROOT)),
        "seed": 20261013,
        "conditions": results,
        "trajectory_comparisons": comparisons,
        "interpretation_limits": [
            "A difference does not establish novelty or causal validity by itself.",
            "No difference may indicate inactive fusion, an insensitive scenario, "
            "or a genuine lack of effect.",
            "Verify that the estimator implements the intended fusion algorithm.",
            "A single seed is diagnostic only; follow with repeated paired seeds.",
        ],
    }

    json_path = AUDIT / "audit_results.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# AeroNet communication-fusion mechanism audit",
        "",
        f"Base configuration: `{config_path.relative_to(ROOT)}`",
        "",
        "| Condition | Fusion | Packet loss | Mean per-agent RMSE |",
        "|---|---:|---:|---:|",
    ]
    for name, method, fusion, loss in conditions:
        rmse = results[name]["mean_agent_rmse"]
        lines.append(
            f"| {name} | {fusion} | {loss:.0%} | {rmse:.8f} |"
        )

    lines += [
        "",
        "## Trajectory comparisons",
        "",
        "```json",
        json.dumps(comparisons, indent=2),
        "```",
        "",
        "## Caution",
        "",
        "This is a diagnostic experiment with one seed. It does not establish "
        "novelty, statistical significance, or a general performance law. "
        "Inspect the estimator and fusion implementation before interpreting "
        "any observed difference.",
    ]

    md_path = AUDIT / "audit_report.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\nAudit completed.")
    print(f"JSON results: {json_path.relative_to(ROOT)}")
    print(f"Report:       {md_path.relative_to(ROOT)}")
    print("\nTrajectory comparisons:")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()

