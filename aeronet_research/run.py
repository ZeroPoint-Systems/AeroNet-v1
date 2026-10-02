from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .io import provenance, write_csv, write_json
from .metrics import aggregate
from .simulation import load_config, run


def execute(config_path: str | Path, output_root: str | Path = "experiments/raw") -> Path:
    config_path = Path(config_path)
    config = load_config(config_path)

    experiment_id = str(config["experiment"]["id"])
    output = Path(output_root) / experiment_id

    if output.exists():
        raise FileExistsError(
            f"Experiment output already exists: {output}. "
            "Raw experiment data are immutable."
        )

    output.mkdir(parents=True)

    result = run(config)

    observations = [
        {
            "agent_id": o.agent_id,
            "time": o.time,
            "truth_x": o.truth.x,
            "truth_y": o.truth.y,
            "observation_x": o.measured.x,
            "observation_y": o.measured.y,
        }
        for o in result.observations
    ]

    communications = [
        {
            "time_sent": p.time_sent,
            "time_delivered": p.time_delivered,
            "sender": p.sender,
            "receiver": p.receiver,
            "delivered": int(p.delivered),
            "latency": p.latency,
            "estimate_x": p.estimate.state.x,
            "estimate_y": p.estimate.state.y,
            "covariance_trace": p.estimate.covariance_trace,
        }
        for p in result.packets
    ]

    metrics = aggregate(
        result.trajectory,
        communications,
    )

    config_copy = output / "config.yaml"
    config_copy.write_text(
        yaml.safe_dump(config, sort_keys=False),
        encoding="utf-8",
    )

    write_csv(output / "observations.csv", observations)
    write_csv(output / "communications.csv", communications)
    write_csv(output / "trajectory.csv", result.trajectory)
    write_csv(output / "metrics.csv", metrics)

    metadata = provenance()
    metadata.update(
        {
            "experiment_id": experiment_id,
            "seed": config["experiment"]["seed"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status": "complete",
        }
    )

    write_json(output / "metadata.json", metadata)

    manifest = {
        "experiment_id": experiment_id,
        "seed": config["experiment"]["seed"],
        "status": "complete",
        "datasets": {
            "observations": "observations.csv",
            "communications": "communications.csv",
            "trajectory": "trajectory.csv",
            "metrics": "metrics.csv",
        },
        "communication": {
            "packets_generated": len(communications),
            "packets_delivered": sum(
                int(p["delivered"]) for p in communications
            ),
            "packets_lost": sum(
                1 - int(p["delivered"]) for p in communications
            ),
        },
        "provenance": metadata,
    }

    write_json(output / "manifest.json", manifest)

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", default="experiments/raw")
    args = parser.parse_args()

    path = execute(args.config, args.output_root)
    print(f"Experiment complete: {path}")


if __name__ == "__main__":
    main()
