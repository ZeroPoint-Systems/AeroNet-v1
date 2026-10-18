from __future__ import annotations

import argparse
import csv
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def covariance_intersection(xa, pa, xb, pb, grid_size=21):
    """Fuse two Gaussian estimates with unknown cross-correlation."""
    ia = np.linalg.solve(pa, np.eye(len(xa)))
    ib = np.linalg.solve(pb, np.eye(len(xb)))

    best = None
    for weight in np.linspace(0.0, 1.0, grid_size):
        information = weight * ia + (1.0 - weight) * ib
        covariance = np.linalg.solve(information, np.eye(len(xa)))
        covariance = (covariance + covariance.T) / 2.0
        mean = covariance @ (weight * ia @ xa + (1.0 - weight) * ib @ xb)
        score = float(np.trace(covariance))
        if best is None or score < best[0]:
            best = (score, mean, covariance, float(weight))

    return best[1], best[2], best[3]


def generate_world(seed, steps, agents, dt):
    """Generate shared ground truth and fixed observations for paired trials."""
    rng = np.random.default_rng(seed)
    truth = np.zeros((steps + 1, 4), dtype=float)
    truth[0] = [0.0, 0.0, 1.0, 0.35]
    observations = np.full((steps, agents, 2), np.nan)

    sensor_std = np.linspace(0.25, 0.8, agents)
    dropout_probability = np.linspace(0.05, 0.25, agents)

    for t in range(steps):
        acceleration = rng.normal(0.0, 0.12, size=2)
        truth[t + 1, :2] = (
            truth[t, :2] + truth[t, 2:] * dt
            + 0.5 * acceleration * dt * dt
        )
        truth[t + 1, 2:] = truth[t, 2:] + acceleration * dt

        for agent in range(agents):
            if rng.random() >= dropout_probability[agent]:
                observations[t, agent] = (
                    truth[t + 1, :2]
                    + rng.normal(0.0, sensor_std[agent], size=2)
                )

    return truth, observations, sensor_std


def update_filter(x, p, observation, sensor_std, dt):
    """One constant-velocity Kalman prediction and optional measurement update."""
    f = np.array([
        [1, 0, dt, 0],
        [0, 1, 0, dt],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ], dtype=float)
    h = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
    g = np.array([
        [dt * dt / 2, 0],
        [0, dt * dt / 2],
        [dt, 0],
        [0, dt],
    ], dtype=float)

    q = g @ (0.12 ** 2 * np.eye(2)) @ g.T
    x = f @ x
    p = f @ p @ f.T + q
    p = (p + p.T) / 2.0
    nis = 0.0

    if np.all(np.isfinite(observation)):
        r = sensor_std ** 2 * np.eye(2)
        innovation = observation - h @ x
        s = h @ p @ h.T + r
        nis = float(innovation @ np.linalg.solve(s, innovation))
        k = np.linalg.solve(s, h @ p).T
        x = x + k @ innovation

        identity = np.eye(4)
        residual = identity - k @ h
        p = residual @ p @ residual.T + k @ r @ k.T
        p = (p + p.T) / 2.0

    return x, p, nis


def run_mode(truth, observations, sensor_std, mode, dt):
    steps, agents, _ = observations.shape
    estimates = np.zeros((steps, agents, 4), dtype=float)

    states = np.zeros((agents, 4), dtype=float)
    covariances = np.repeat(
        np.diag([25.0, 25.0, 9.0, 9.0])[None, :, :],
        agents, axis=0
    )
    recent_innovations = np.zeros(agents, dtype=float)
    messages = 0

    for t in range(steps):
        for agent in range(agents):
            states[agent], covariances[agent], recent_innovations[agent] = (
                update_filter(
                    states[agent],
                    covariances[agent],
                    observations[t, agent],
                    sensor_std[agent],
                    dt,
                )
            )

        if mode == "periodic":
            sender = t % agents
            receiver = (sender + 1) % agents

        elif mode == "adaptive":
            # Experimental heuristic, not a claimed novel algorithm:
            # send from the most certain agent to the agent with the
            # highest local uncertainty, weighted by its recent innovation.
            uncertainty = np.trace(covariances, axis1=1, axis2=2)
            risk = uncertainty * (
                1.0 + 0.1 * np.minimum(recent_innovations, 10.0)
            )
            sender = int(np.argmin(uncertainty))
            ranked = np.argsort(risk)
            receiver = int(ranked[-1])
            if receiver == sender:
                receiver = int(ranked[-2])

        elif mode == "none":
            sender = receiver = -1

        else:
            raise ValueError(f"Unknown mode: {mode}")

        if sender >= 0:
            states[receiver], covariances[receiver], _ = covariance_intersection(
                states[receiver], covariances[receiver],
                states[sender], covariances[sender],
            )
            messages += 1

        estimates[t] = states

    position_error = estimates[:, :, :2] - truth[1:, None, :2]
    rmse_by_time = np.sqrt(np.mean(np.sum(position_error ** 2, axis=2), axis=1))
    return float(np.mean(rmse_by_time)), rmse_by_time, messages


def self_test():
    mean, covariance, weight = covariance_intersection(
        np.array([0.0]), np.array([[1.0]]),
        np.array([2.0]), np.array([[4.0]])
    )
    assert mean.shape == (1,)
    assert covariance.shape == (1, 1)
    assert np.linalg.eigvalsh(covariance).min() > 0
    assert 0.0 <= weight <= 1.0

    truth, observations, sensor_std = generate_world(7, 10, 3, 0.1)
    score, curve, messages = run_mode(
        truth, observations, sensor_std, "adaptive", 0.1
    )
    assert math.isfinite(score)
    assert len(curve) == 10
    assert messages == 10
    print("Internal numerical and integration smoke tests passed.")


def write_svg(path, curves, title, y_label):
    width, height = 1000, 560
    left, right, top, bottom = 90, 35, 65, 75
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(float(np.max(values)) for values in curves.values())
    maximum = max(maximum * 1.12, 1e-9)

    palette = {
        "none": "#555555",
        "periodic": "#2369a8",
        "adaptive": "#b04a35",
    }

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="32" text-anchor="middle" '
        f'font-size="21" font-family="sans-serif">{title}</text>',
    ]

    for tick in range(6):
        y_value = maximum * tick / 5
        y = top + plot_height * (1 - tick / 5)
        parts.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" '
            f'y2="{y:.2f}" stroke="#dddddd"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{y+5:.2f}" text-anchor="end" '
            f'font-size="13" font-family="sans-serif">{y_value:.3f}</text>'
        )

    for name, values in curves.items():
        n = len(values)
        points = []
        for index, value in enumerate(values):
            x = left + plot_width * index / max(n - 1, 1)
            y = top + plot_height * (1 - value / maximum)
            points.append(f"{x:.2f},{y:.2f}")
        parts.append(
            f'<polyline fill="none" stroke="{palette[name]}" stroke-width="2.5" '
            f'points="{" ".join(points)}"/>'
        )

    parts.extend([
        f'<text x="{left+plot_width/2}" y="{height-25}" text-anchor="middle" '
        'font-size="15" font-family="sans-serif">Time step</text>',
        f'<text x="22" y="{top+plot_height/2}" transform="rotate(-90 22 '
        f'{top+plot_height/2})" text-anchor="middle" font-size="15" '
        f'font-family="sans-serif">{y_label}</text>',
    ])

    for index, name in enumerate(curves):
        x = left + index * 190
        parts.append(
            f'<line x1="{x}" y1="{height-52}" x2="{x+28}" '
            f'y2="{height-52}" stroke="{palette[name]}" stroke-width="3"/>'
        )
        parts.append(
            f'<text x="{x+36}" y="{height-47}" font-size="14" '
            f'font-family="sans-serif">{name}</text>'
        )

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--agents", type=int, default=6)
    parser.add_argument("--dt", type=float, default=0.1)
    args = parser.parse_args()

    if args.seeds < 2 or args.steps < 10 or args.agents < 3 or args.dt <= 0:
        raise SystemExit("Use at least 2 seeds, 10 steps, 3 agents and positive dt.")

    self_test()

    output = Path(__file__).resolve().parent / "runs" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    output.mkdir(parents=True, exist_ok=False)

    modes = ("none", "periodic", "adaptive")
    trial_rows = []
    curves = {mode: [] for mode in modes}

    for seed in range(args.seeds):
        truth, observations, sensor_std = generate_world(
            seed, args.steps, args.agents, args.dt
        )

        for mode in modes:
            rmse, curve, messages = run_mode(
                truth, observations, sensor_std, mode, args.dt
            )
            trial_rows.append({
                "seed": seed,
                "mode": mode,
                "mean_position_rmse": rmse,
                "messages": messages,
                "steps": args.steps,
                "agents": args.agents,
            })
            curves[mode].append(curve)

        print(f"Completed paired seed {seed + 1}/{args.seeds}")

    with (output / "trial_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=trial_rows[0].keys())
        writer.writeheader()
        writer.writerows(trial_rows)

    mean_curves = {
        mode: np.mean(np.stack(curves[mode]), axis=0)
        for mode in modes
    }

    with (output / "rmse_by_time.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["step", *modes])
        for step in range(args.steps):
            writer.writerow([
                step + 1, *(float(mean_curves[m][step]) for m in modes)
            ])

    summaries = {}
    for mode in modes:
        values = np.array([
            row["mean_position_rmse"] for row in trial_rows
            if row["mode"] == mode
        ])
        summaries[mode] = {
            "mean_rmse": float(np.mean(values)),
            "sd_rmse": float(np.std(values, ddof=1)),
            "mean_messages_per_trial": float(
                np.mean([row["messages"] for row in trial_rows
                         if row["mode"] == mode])
            ),
        }

    periodic = np.array([
        row["mean_position_rmse"] for row in trial_rows
        if row["mode"] == "periodic"
    ])
    adaptive = np.array([
        row["mean_position_rmse"] for row in trial_rows
        if row["mode"] == "adaptive"
    ])
    differences = adaptive - periodic

    bootstrap_rng = np.random.default_rng(20261017)
    bootstrap_means = np.array([
        np.mean(bootstrap_rng.choice(differences, size=len(differences), replace=True))
        for _ in range(5000)
    ])

    summary = {
        "status": "exploratory simulation; not evidence of novelty",
        "configuration": vars(args),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "trials_per_mode": args.seeds,
        "summary": summaries,
        "paired_adaptive_minus_periodic_rmse": {
            "mean_difference": float(np.mean(differences)),
            "bootstrap_95_percent_interval": [
                float(np.quantile(bootstrap_means, 0.025)),
                float(np.quantile(bootstrap_means, 0.975)),
            ],
            "interpretation": (
                "Negative values favour adaptive; positive values favour periodic. "
                "This exploratory interval is not proof of a novel contribution."
            ),
        },
    }

    (output / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    write_svg(
        output / "rmse_plot.svg",
        mean_curves,
        "AeroNet exploratory tracking benchmark",
        "Mean position RMSE",
    )

    report = [
        "# AeroNet exploratory tracking benchmark",
        "",
        "This is an initial synthetic benchmark, not a novelty claim.",
        "",
        f"- Agents: {args.agents}",
        f"- Steps per trial: {args.steps}",
        f"- Paired seeds: {args.seeds}",
        "",
        "## Mean RMSE",
    ]
    for mode, values in summaries.items():
        report.append(
            f"- {mode}: {values['mean_rmse']:.6f} "
            f"(SD {values['sd_rmse']:.6f}); "
            f"mean messages {values['mean_messages_per_trial']:.1f}"
        )

    report.extend([
        "",
        "## Adaptive minus periodic",
        f"- Mean paired difference: {np.mean(differences):.6f}",
        "- Bootstrap interval: "
        f"{summary['paired_adaptive_minus_periodic_rmse']['bootstrap_95_percent_interval']}",
        "",
        "## Files",
        "- trial_results.csv: per-seed results",
        "- rmse_by_time.csv: time-series averages",
        "- rmse_plot.svg: generated figure",
        "- summary.json: configuration and summary statistics",
        "",
        "## Limitations",
        "- Synthetic constant-velocity target and simplified sensor model.",
        "- Centralised policy selection is used for this exploratory comparison.",
        "- The adaptive heuristic is not claimed as novel.",
        "- No Gazebo, ROS 2 or physical flight validation is included.",
        "- Further baselines, model checks, and independent validation are required.",
    ])
    (output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print("\nResults written to:", output)
    print((output / "REPORT.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
