from __future__ import annotations

import argparse
import json
from pathlib import Path

from .protocol import build_protocol


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/scientific_campaign"),
    )

    parser.add_argument(
        "--replicates",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20261007,
    )

    args = parser.parse_args()

    experiments = build_protocol(
        measurement_noise=[0.5, 1.0, 2.0],
        communication_range=[10.0, 25.0, 50.0],
        packet_loss_probability=[0.0, 0.05, 0.20],
        latency=[0.0, 0.1, 0.5],
        number_of_agents=[4],
        replicates=args.replicates,
        base_seed=args.seed,
        baselines=[
            "aeronet",
            "no_communication",
            "centralised",
        ],
    )

    args.output.mkdir(parents=True, exist_ok=True)

    path = args.output / "protocol.json"

    path.write_text(
        json.dumps(
            {
                "base_seed": args.seed,
                "replicates": args.replicates,
                "experiments": [
                    {
                        "experiment_id": experiment.experiment_id(),
                        **experiment.as_dict(),
                    }
                    for experiment in experiments
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print(f"Scientific protocol written to {path}")
    print(f"Experiments defined: {len(experiments)}")


if __name__ == "__main__":
    main()
