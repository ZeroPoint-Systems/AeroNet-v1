from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from experiments.runners.run_experiment import run as run_experiment


@dataclass(frozen=True)
class ScientificRun:
    condition_id: str
    replicate: int
    baseline: str
    seed: int
    config_path: Path
    output_path: Path


def build_config(
    base_config: Path,
    output_config: Path,
    condition: dict[str, Any],
) -> Path:
    with base_config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError("Base configuration must contain a YAML mapping")

    config.setdefault("experiment", {})
    config.setdefault("sensing", {})
    config.setdefault("communication", {})
    config.setdefault("swarm", {})

    config["experiment"]["id"] = condition["condition_id"]
    config["experiment"]["seed"] = int(condition["seed"])

    config["sensing"]["measurement_noise"] = float(
        condition["measurement_noise"]
    )

    config["communication"]["range"] = float(
        condition["communication_range"]
    )

    config["communication"]["packet_loss_probability"] = float(
        condition["packet_loss_probability"]
    )

    config["communication"]["latency"] = float(
        condition["communication_latency"]
    )

    config["swarm"]["number_of_agents"] = int(
        condition["number_of_agents"]
    )

    output_config.parent.mkdir(parents=True, exist_ok=True)

    with output_config.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)

    return output_config


def run_scientific_experiment(
    base_config: Path,
    output_root: Path,
    condition: dict[str, Any],
) -> ScientificRun:
    condition_id = str(condition["condition_id"])
    replicate = int(condition["replicate"])
    baseline = str(condition["baseline"])
    seed = int(condition["seed"])

    config_path = (
        output_root
        / "configs"
        / f"{condition_id}_r{replicate}_{baseline}.yaml"
    )

    result_root = (
        output_root
        / "runs"
        / condition_id
        / f"replicate_{replicate}"
        / baseline
    )

    build_config(
        base_config=base_config,
        output_config=config_path,
        condition=condition,
    )

    result_root.mkdir(parents=True, exist_ok=True)

    raw_output = run_experiment(
        str(config_path),
        output_root=result_root,
    )

    manifest = {
        "condition_id": condition_id,
        "replicate": replicate,
        "baseline": baseline,
        "seed": seed,
        "config": str(config_path),
        "raw_output": str(raw_output),
    }

    manifest_path = result_root / "scientific_manifest.json"

    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    return ScientificRun(
        condition_id=condition_id,
        replicate=replicate,
        baseline=baseline,
        seed=seed,
        config_path=config_path,
        output_path=Path(raw_output),
    )
