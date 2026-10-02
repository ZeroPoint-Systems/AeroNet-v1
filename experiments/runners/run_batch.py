from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

import yaml


def stable_seed(base_seed: int, index: int) -> int:
    payload = f"{base_seed}:{index}".encode()
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % (2**32)


def set_nested(data, dotted_key, value):
    parts = dotted_key.split(".")
    target = data
    for part in parts[:-1]:
        if part not in target or not isinstance(target[part], dict):
            target[part] = {}
        target = target[part]
    target[parts[-1]] = value


def get_nested(data, dotted_key):
    target = data
    for part in dotted_key.split("."):
        target = target[part]
    return target


def expand_grid(grid):
    keys = list(grid)
    values = [grid[k] for k in keys]
    for combination in itertools.product(*values):
        yield dict(zip(keys, combination))


def load_batch(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_batch(batch_path):
    root = Path.cwd()
    batch_path = Path(batch_path)
    batch = load_batch(batch_path)

    base_config_path = root / batch["base_config"]
    output_root = root / batch.get("output_root", "experiments/raw")
    batch_id = batch.get("batch_id", batch_path.stem)
    base_seed = int(batch.get("seed", 12345))
    grid = batch.get("grid", {})

    with open(base_config_path, "r", encoding="utf-8") as f:
        base = yaml.safe_load(f)

    combinations = list(expand_grid(grid))
    if not combinations:
        combinations = [{}]

    batch_output = root / "experiments" / "batches" / batch_id
    configs_dir = batch_output / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)

    records = []

    for index, overrides in enumerate(combinations):
        config = copy.deepcopy(base)

        for key, value in overrides.items():
            set_nested(config, key, value)

        seed = stable_seed(base_seed, index)
        experiment_id = f"{batch_id}_{index:04d}_{seed}"

        config["experiment"]["id"] = experiment_id
        config["experiment"]["seed"] = seed

        config_path = configs_dir / f"{experiment_id}.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False)

        command = [
            sys.executable,
            "-m",
            "experiments.runners.run_experiment",
            "--config",
            str(config_path),
        ]

        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
        )

        record = {
            "experiment_id": experiment_id,
            "seed": seed,
            "overrides": overrides,
            "config": str(config_path),
            "returncode": result.returncode,
            "status": "complete" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        records.append(record)

        with open(batch_output / "batch_progress.json", "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise RuntimeError(f"Experiment failed: {experiment_id}")

    summary = {
        "batch_id": batch_id,
        "base_config": str(base_config_path),
        "number_of_experiments": len(records),
        "completed": sum(r["status"] == "complete" for r in records),
        "failed": sum(r["status"] == "failed" for r in records),
        "experiments": records,
    }

    with open(batch_output / "batch_manifest.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"batch complete: {batch_id}")
    print(f"experiments: {len(records)}")
    print(f"output: {batch_output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run_batch(args.config)


if __name__ == "__main__":
    main()
