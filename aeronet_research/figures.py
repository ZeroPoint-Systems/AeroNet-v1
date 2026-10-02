from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_figures(batch_directory: str | Path) -> None:
    directory = Path(batch_directory)

    summary = pd.read_csv(directory / "summary.csv")

    figure_directory = directory / "figures"
    figure_directory.mkdir(exist_ok=True)

    plt.figure()
    for experiment_id, frame in summary.groupby("experiment_id"):
        plt.plot(
            frame["agent_id"],
            frame["rmse"],
            marker="o",
            label=experiment_id,
        )

    plt.xlabel("Agent")
    plt.ylabel("RMSE")
    plt.title("Estimation RMSE by experiment")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_directory / "rmse_by_experiment.png", dpi=300)
    plt.close()

    statistics = pd.read_csv(directory / "statistics.csv")

    plt.figure()
    plt.errorbar(
        statistics["metric"],
        statistics["mean"],
        yerr=[
            statistics["mean"] - statistics["ci_95_lower"],
            statistics["ci_95_upper"] - statistics["mean"],
        ],
        fmt="o",
    )

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Estimate")
    plt.title("Metric estimates with 95% bootstrap confidence intervals")
    plt.tight_layout()
    plt.savefig(
        figure_directory / "bootstrap_confidence_intervals.png",
        dpi=300,
    )
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    make_figures(args.directory)


if __name__ == "__main__":
    main()
