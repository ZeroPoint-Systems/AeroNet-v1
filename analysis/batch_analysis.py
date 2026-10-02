from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def analyse(batch_manifest):
    manifest_path = Path(batch_manifest)
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    rows = []

    for experiment in manifest["experiments"]:
        if experiment["status"] != "complete":
            continue

        experiment_id = experiment["experiment_id"]
        result_dir = Path("experiments/raw") / experiment_id
        metrics_path = result_dir / "metrics.csv"

        if not metrics_path.exists():
            continue

        with open(metrics_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            metrics = list(reader)

        for row in metrics:
            row["experiment_id"] = experiment_id
            row["seed"] = experiment["seed"]
            for key, value in experiment["overrides"].items():
                row[key] = value
            rows.append(row)

    output = manifest_path.parent / "summary.csv"

    if rows:
        fields = []
        for row in rows:
            for field in row:
                if field not in fields:
                    fields.append(field)

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"analysis complete: {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    analyse(args.manifest)


if __name__ == "__main__":
    main()
