from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def bootstrap_mean(
    values,
    n: int = 5000,
    seed: int = 12345,
):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")

    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0,
        len(values),
        size=(n, len(values)),
    )

    means = values[indices].mean(axis=1)

    return (
        float(values.mean()),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def discover_runs(manifest: dict):
    """
    Normalise both supported batch-manifest schemas into:

        {
            experiment_id,
            seed,
            replicate,
            overrides
        }
    """

    if "runs" in manifest:
        return manifest["runs"]

    # Legacy AeroNet batch-runner format.
    experiments = manifest.get("experiments")

    if experiments is None:
        experiments = manifest.get("results")

    if experiments is None:
        raise ValueError(
            "Batch manifest contains neither 'runs' nor a recognised "
            "legacy experiment list."
        )

    normalised = []

    for index, item in enumerate(experiments):
        if isinstance(item, str):
            experiment_id = item
            seed = None
            overrides = {}
            replicate = 0
        else:
            experiment_id = (
                item.get("experiment_id")
                or item.get("id")
                or item.get("name")
            )

            if experiment_id is None:
                raise ValueError(
                    f"Manifest experiment {index} has no experiment_id."
                )

            seed = item.get("seed")
            overrides = item.get("overrides", {})
            replicate = item.get("replicate", 0)

        normalised.append(
            {
                "experiment_id": experiment_id,
                "seed": seed,
                "replicate": replicate,
                "overrides": overrides,
            }
        )

    return normalised


def locate_metrics(root: Path, experiment_id: str):
    candidates = [
        root / "experiments" / "raw" / experiment_id / "metrics.csv",
        root / "experiments" / "raw" / experiment_id / "metrics.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find metrics.csv for experiment '{experiment_id}'."
    )


def analyse(manifest_path: str | Path) -> Path:
    manifest_path = Path(manifest_path)
    manifest = read_json(manifest_path)

    root = Path.cwd()
    runs = discover_runs(manifest)

    if not runs:
        raise ValueError("Batch manifest contains zero experiments.")

    frames = []

    for run in runs:
        experiment_id = str(run["experiment_id"])
        metrics_path = locate_metrics(root, experiment_id)

        frame = pd.read_csv(metrics_path)

        frame["experiment_id"] = experiment_id

        if run.get("seed") is not None:
            frame["seed"] = run["seed"]

        frame["replicate"] = run.get("replicate", 0)

        overrides = run.get("overrides", {})

        if isinstance(overrides, dict):
            for key, value in overrides.items():
                column = "parameter__" + key.replace(".", "__")
                frame[column] = value

        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)

    output_directory = manifest_path.parent
    output_directory.mkdir(parents=True, exist_ok=True)

    combined.to_csv(
        output_directory / "summary.csv",
        index=False,
    )

    numeric_metrics = [
        column
        for column in [
            "rmse",
            "mae",
            "final_error",
            "mean_covariance_trace",
            "final_covariance_trace",
            "realised_loss_rate",
        ]
        if column in combined.columns
    ]

    group_columns = [
        "experiment_id",
        "seed",
        "replicate",
    ]

    group_columns = [
        column
        for column in group_columns
        if column in combined.columns
    ]

    aggregations = {}

    for metric in numeric_metrics:
        aggregations[f"{metric}_mean"] = (metric, "mean")
        aggregations[f"{metric}_sd"] = (metric, "std")

    experiment_summary = (
        combined
        .groupby(group_columns, dropna=False)
        .agg(**aggregations)
        .reset_index()
    )

    experiment_summary.to_csv(
        output_directory / "experiment_summary.csv",
        index=False,
    )

    statistics = []

    for metric in numeric_metrics:
        mean, lower, upper = bootstrap_mean(
            combined[metric].dropna().to_numpy()
        )

        statistics.append(
            {
                "metric": metric,
                "mean": mean,
                "ci_95_lower": lower,
                "ci_95_upper": upper,
                "n": int(combined[metric].notna().sum()),
            }
        )

    pd.DataFrame(statistics).to_csv(
        output_directory / "statistics.csv",
        index=False,
    )

    analysis_manifest = {
        "batch_id": manifest.get("batch_id", output_directory.name),
        "input_manifest": str(manifest_path),
        "number_of_experiments": len(runs),
        "number_of_metric_rows": len(combined),
        "bootstrap_samples": 5000,
        "confidence_level": 0.95,
        "outputs": [
            "summary.csv",
            "experiment_summary.csv",
            "statistics.csv",
        ],
    }

    (output_directory / "analysis_manifest.json").write_text(
        json.dumps(
            analysis_manifest,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return output_directory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    output = analyse(args.manifest)
    print(f"Analysis complete: {output}")


if __name__ == "__main__":
    main()
