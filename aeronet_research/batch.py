from __future__ import annotations

import argparse
import copy
import itertools
import subprocess
from pathlib import Path

import yaml

from .io import stable_seed, write_json


def set_nested(data: dict, path: str, value) -> None:
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value


def expand_grid(grid: dict):
    if not grid:
        yield {}
        return

    keys = list(grid)

    values = [
        grid[key] if isinstance(grid[key], list) else [grid[key]]
        for key in keys
    ]

    for combination in itertools.product(*values):
        yield dict(zip(keys, combination))


def run_batch(path: str | Path) -> Path:
    path = Path(path)
    root = Path.cwd()

    with path.open(encoding="utf-8") as handle:
        batch = yaml.safe_load(handle)

    batch_id = batch["batch_id"]
    base_path = root / batch["base_config"]

    with base_path.open(encoding="utf-8") as handle:
        base = yaml.safe_load(handle)

    batch_root = root / "experiments" / "batches" / batch_id
    config_root = batch_root / "configs"
    batch_root.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)

    runs = list(expand_grid(batch.get("grid", {})))
    replicates = int(batch.get("replicates", 1))
    base_seed = int(batch.get("seed", base["experiment"]["seed"]))

    records = []

    index = 0

    for override in runs:
        for replicate in range(replicates):
            config = copy.deepcopy(base)

            for parameter, value in override.items():
                set_nested(config, parameter, value)

            seed = stable_seed(base_seed, index)

            config["experiment"]["seed"] = seed
            config["experiment"]["id"] = (
                f"{batch_id}_{index:04d}_{seed}"
            )

            config_path = config_root / f"{config['experiment']['id']}.yaml"

            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False),
                encoding="utf-8",
            )

            output = root / "experiments" / "raw" / config["experiment"]["id"]

            if not output.exists():
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "aeronet_research.run",
                        "--config",
                        str(config_path),
                    ],
                    check=True,
                )

            records.append(
                {
                    "index": index,
                    "experiment_id": config["experiment"]["id"],
                    "seed": seed,
                    "replicate": replicate,
                    "overrides": override,
                    "status": "complete",
                }
            )

            write_json(
                batch_root / "batch_progress.json",
                {
                    "batch_id": batch_id,
                    "completed": len(records),
                    "total": len(runs) * replicates,
                    "runs": records,
                },
            )

            index += 1

    manifest = {
        "batch_id": batch_id,
        "base_config": str(batch["base_config"]),
        "seed": base_seed,
        "replicates": replicates,
        "total_runs": len(records),
        "runs": records,
    }

    manifest_path = batch_root / "batch_manifest.json"
    write_json(manifest_path, manifest)

    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    print(run_batch(args.config))


if __name__ == "__main__":
    main()
