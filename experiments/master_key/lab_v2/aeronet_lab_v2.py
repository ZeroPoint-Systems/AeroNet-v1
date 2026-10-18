from __future__ import annotations

import csv
import json
import math
import random
import sys
import time
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("Missing dependency: numpy")
    print("Install it with: python -m pip install numpy")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
OUT = ROOT / "runs" / RUN_ID
OUT.mkdir(parents=True, exist_ok=False)

SEEDS = list(range(20261020, 20261040))
AGENTS = 6
STEPS = 300
WINDOW = 5
PACKET_LOSS = 0.10
MIN_DELAY = 1
MAX_DELAY = 3
POLICIES = ("none", "periodic", "reactive", "predictive")

DT = 1.0
F = np.array([
    [1, 0, DT, 0],
    [0, 1, 0, DT],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
], dtype=float)

H = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
], dtype=float)

Q = np.diag([0.05, 0.05, 0.08, 0.08])
R = np.diag([2.0, 2.0])
R_INV = np.linalg.inv(R)

def symmetrise(P):
    return 0.5 * (P + P.T)

def predict_state(x, P, count=1):
    for _ in range(count):
        x = F @ x
        P = symmetrise(F @ P @ F.T + Q)
    return x, P

def kalman_update(x, P, z):
    innovation = z - H @ x
    S = symmetrise(H @ P @ H.T + R)
    K = P @ H.T @ np.linalg.inv(S)
    x_new = x + K @ innovation
    I = np.eye(4)
    # Joseph form improves numerical stability.
    A = I - K @ H
    P_new = A @ P @ A.T + K @ R @ K.T
    nis = float(innovation.T @ np.linalg.solve(S, innovation))
    return x_new, symmetrise(P_new), nis

def covariance_intersection(x1, P1, x2, P2):
    """
    Conservative pairwise Gaussian fusion for unknown cross-correlation.
    This prototype uses a fixed weight grid and does not claim a novel
    fusion algorithm.
    """
    I1 = np.linalg.inv(P1)
    I2 = np.linalg.inv(P2)
    best = None

    for w in np.linspace(0.0, 1.0, 21):
        precision = symmetrise(w * I1 + (1.0 - w) * I2)
        try:
            P = symmetrise(np.linalg.inv(precision))
            sign, logdet = np.linalg.slogdet(P)
            if sign <= 0 or not np.isfinite(logdet):
                continue
            x = P @ (w * I1 @ x1 + (1.0 - w) * I2 @ x2)
            if best is None or logdet < best[0]:
                best = (logdet, x, P)
        except np.linalg.LinAlgError:
            continue

    if best is None:
        raise RuntimeError("Covariance intersection failed numerically.")

    return best[1], best[2]

def make_world(seed):
    """
    Generate shared ground truth and sensor observations before running
    any policy. Every policy for a seed sees the same observations.
    """
    rng = np.random.default_rng(seed)
    truth = np.zeros((STEPS, 4), dtype=float)
    truth[0] = np.array([0.0, 0.0, 1.0, -0.4])

    for t in range(1, STEPS):
        acceleration = rng.normal(0.0, 0.12, size=2)
        truth[t] = F @ truth[t - 1]
        truth[t, 2:] += acceleration

    observations = np.zeros((STEPS, AGENTS, 2), dtype=float)
    for t in range(STEPS):
        for i in range(AGENTS):
            observations[t, i] = H @ truth[t] + rng.multivariate_normal(
                np.zeros(2), R
            )

    return truth, observations

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.x = np.zeros(4, dtype=float)
        self.P = np.diag([20.0, 20.0, 10.0, 10.0])
        self.innovation_ema = 1.0
        self.previous_ema = 1.0
        self.initialised = False
        self.last_sent_window = -1
        self.nis = 0.0
        self.risk = 0.0

    def update(self, observation):
        if not self.initialised:
            self.x[:2] = observation
            self.x[2:] = 0.0
            self.P = np.diag([2.0, 2.0, 10.0, 10.0])
            self.initialised = True
            self.nis = 0.0
        else:
            self.x, self.P = predict_state(self.x, self.P)
            self.x, self.P, self.nis = kalman_update(
                self.x, self.P, observation
            )

        self.previous_ema = self.innovation_ema
        self.innovation_ema = (
            0.7 * self.innovation_ema + 0.3 * self.nis
        )

        position_uncertainty = float(np.trace(self.P[:2, :2]))
        trend = max(0.0, self.innovation_ema - self.previous_ema)

        # Fixed exploratory score. It must be evaluated and calibrated,
        # not presented as an established predictive model.
        self.risk = (
            0.50 * min(4.0, position_uncertainty / 2.0)
            + 0.35 * min(4.0, self.innovation_ema / 2.0)
            + 0.15 * min(4.0, trend * 2.0)
        )

def should_send(policy, agent, t):
    if policy == "none":
        return False

    if policy == "periodic":
        return t % WINDOW == 0

    window_end = ((t // WINDOW) + 1) * WINDOW - 1

    # At most one transmission per agent per window.
    if agent.last_sent_window == t // WINDOW:
        return False

    if policy == "reactive":
        trigger = (
            float(np.trace(agent.P[:2, :2])) > 3.0
            or agent.nis > 5.0
        )
    elif policy == "predictive":
        trigger = agent.risk > 1.15
    else:
        raise ValueError(f"Unknown policy: {policy}")

    # The final step is a fallback. This makes the transmission
    # opportunity count equal across the three communicating policies.
    return trigger or t == window_end

def run_trial(seed, policy, truth, observations):
    agents = [Agent(i) for i in range(AGENTS)]
    network_rng = random.Random(seed + 700_000)
    queue = []
    attempted = 0
    delivered = 0
    dropped = 0
    peak_queue = 0
    errors = []

    for t in range(STEPS):
        for i, agent in enumerate(agents):
            agent.update(observations[t, i])

        # Deliver messages scheduled for this time. Each message contains
        # a historical state estimate; propagate it to the current time.
        due = [m for m in queue if m["due"] <= t]
        queue = [m for m in queue if m["due"] > t]

        for message in due:
            receiver = agents[message["receiver"]]
            age = t - message["sent"]
            incoming_x, incoming_P = predict_state(
                message["x"].copy(), message["P"].copy(), age
            )
            receiver.x, receiver.P = covariance_intersection(
                receiver.x, receiver.P, incoming_x, incoming_P
            )
            delivered += 1

        for agent in agents:
            if should_send(policy, agent, t):
                agent.last_sent_window = t // WINDOW
                if policy == "periodic":
                    # Periodic decisions are fixed at the start of each
                    # communication window.
                    pass

                attempted += 1

                for receiver_id in range(AGENTS):
                    if receiver_id == agent.id:
                        continue

                    if network_rng.random() < PACKET_LOSS:
                        dropped += 1
                        continue

                    delay = network_rng.randint(MIN_DELAY, MAX_DELAY)
                    queue.append({
                        "due": t + delay,
                        "sent": t,
                        "sender": agent.id,
                        "receiver": receiver_id,
                        "x": agent.x.copy(),
                        "P": agent.P.copy(),
                    })

        peak_queue = max(peak_queue, len(queue))

        for agent in agents:
            position_error = agent.x[:2] - truth[t, :2]
            errors.append(float(position_error @ position_error))

    # Messages still in the queue at the end are not counted as delivered.
    rmse = math.sqrt(sum(errors) / len(errors))

    return {
        "seed": seed,
        "policy": policy,
        "rmse": rmse,
        "attempted_messages": attempted,
        "delivered_links": delivered,
        "dropped_links": dropped,
        "undelivered_at_end": len(queue),
        "peak_queue": peak_queue,
    }

def bootstrap_interval(values, repetitions=5000, seed=91357):
    rng = random.Random(seed)
    values = list(values)
    if not values:
        return [None, None]
    means = []
    for _ in range(repetitions):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort()
    return [
        means[int(0.025 * repetitions)],
        means[min(repetitions - 1, int(0.975 * repetitions))],
    ]

def write_svg(summary, path):
    policies = list(POLICIES)
    values = [summary[p]["mean_rmse"] for p in policies]
    width, height = 850, 470
    left, bottom, top = 100, 370, 70
    plot_h = bottom - top
    max_value = max(values) * 1.20 if values else 1.0
    bar_w = 105
    gap = 65
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="425" y="35" font-size="22" text-anchor="middle" font-family="Arial">AeroNet Lab v2: mean position RMSE</text>',
        f'<line x1="{left}" y1="{bottom}" x2="790" y2="{bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="black"/>',
        '<text x="25" y="220" transform="rotate(-90 25 220)" font-size="15" text-anchor="middle" font-family="Arial">RMSE</text>',
    ]
    for i, (name, value) in enumerate(zip(policies, values)):
        x = left + 45 + i * (bar_w + gap)
        bar_h = value / max_value * plot_h
        y = bottom - bar_h
        parts.append(
            f'<rect x="{x}" y="{y:.2f}" width="{bar_w}" height="{bar_h:.2f}" fill="#4779a8"/>'
        )
        parts.append(
            f'<text x="{x + bar_w/2}" y="{y - 8:.2f}" text-anchor="middle" font-size="13" font-family="Arial">{value:.4f}</text>'
        )
        parts.append(
            f'<text x="{x + bar_w/2}" y="{bottom + 25}" text-anchor="middle" font-size="13" font-family="Arial">{name}</text>'
        )
    parts.append(
        '<text x="425" y="440" font-size="12" text-anchor="middle" font-family="Arial">Exploratory synthetic benchmark. Lower is better.</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")

def main():
    rows = []

    print("AeroNet Lab v2")
    print(f"Seeds: {len(SEEDS)} | agents: {AGENTS} | steps: {STEPS}")
    print(f"Network: {PACKET_LOSS:.0%} per-link packet loss, delay {MIN_DELAY}-{MAX_DELAY} steps")
    print("Generating paired trials...")

    for seed in SEEDS:
        truth, observations = make_world(seed)
        for policy in POLICIES:
            row = run_trial(seed, policy, truth, observations)
            rows.append(row)
            print(
                f"seed={seed} policy={policy:10s} "
                f"RMSE={row['rmse']:.5f} "
                f"tx={row['attempted_messages']} "
                f"delivered_links={row['delivered_links']}"
            )

    csv_path = OUT / "trial_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        values = [r["rmse"] for r in subset]
        summary[policy] = {
            "n": len(values),
            "mean_rmse": float(np.mean(values)),
            "sd_rmse": float(np.std(values, ddof=1)),
            "rmse_bootstrap_95_interval": bootstrap_interval(values),
            "mean_attempted_messages": float(np.mean([
                r["attempted_messages"] for r in subset
            ])),
            "mean_delivered_links": float(np.mean([
                r["delivered_links"] for r in subset
            ])),
            "mean_dropped_links": float(np.mean([
                r["dropped_links"] for r in subset
            ])),
        }

    by_seed = {}
    for row in rows:
        by_seed.setdefault(row["seed"], {})[row["policy"]] = row["rmse"]

    comparisons = {}
    for a, b in [
        ("predictive", "reactive"),
        ("predictive", "periodic"),
        ("reactive", "periodic"),
    ]:
        differences = [
            by_seed[s][a] - by_seed[s][b] for s in SEEDS
        ]
        comparisons[f"{a}_minus_{b}"] = {
            "mean_paired_difference": float(np.mean(differences)),
            "paired_bootstrap_95_interval": bootstrap_interval(differences),
            "fraction_seeds_a_better": float(np.mean([
                d < 0 for d in differences
            ])),
        }

    result = {
        "run_id": RUN_ID,
        "status": "exploratory; not a novelty claim",
        "settings": {
            "seeds": SEEDS,
            "agents": AGENTS,
            "steps": STEPS,
            "communication_window": WINDOW,
            "packet_loss_per_link": PACKET_LOSS,
            "delay_steps": [MIN_DELAY, MAX_DELAY],
            "policies": list(POLICIES),
        },
        "summary": summary,
        "paired_comparisons": comparisons,
        "limitations": [
            "Synthetic constant-velocity tracking with stochastic acceleration.",
            "Abstract agents, not physical drones.",
            "Covariance intersection is a simplified reference fusion method.",
            "Predictive score is a fixed heuristic and is not yet calibrated.",
            "Communication cost is measured as attempted broadcasts and delivered links.",
            "One transmission opportunity per agent per window matches counts, but does not establish optimal scheduling.",
            "No literature review or novelty claim is included.",
            "Held-out scenario families and formal hypothesis testing remain future work.",
        ],
    }

    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    write_svg(summary, OUT / "rmse_comparison.svg")

    lines = [
        "# AeroNet Lab v2 exploratory results",
        "",
        "This is a software benchmark, not a novelty claim.",
        "",
        f"- Paired seeds: {len(SEEDS)}",
        f"- Agents: {AGENTS}",
        f"- Steps per trial: {STEPS}",
        f"- Packet loss per link: {PACKET_LOSS:.0%}",
        f"- Delay: {MIN_DELAY}-{MAX_DELAY} steps",
        "",
        "## Mean position RMSE",
        "",
        "| Policy | Mean RMSE | SD | Mean attempted broadcasts | Mean delivered links |",
        "|---|---:|---:|---:|---:|",
    ]

    for policy in POLICIES:
        s = summary[policy]
        lines.append(
            f"| {policy} | {s['mean_rmse']:.6f} | {s['sd_rmse']:.6f} | "
            f"{s['mean_attempted_messages']:.1f} | {s['mean_delivered_links']:.1f} |"
        )

    lines.extend(["", "## Paired comparisons", ""])
    for name, values in comparisons.items():
        lines.append(
            f"- **{name}:** mean difference "
            f"{values['mean_paired_difference']:.6f}; bootstrap interval "
            f"{values['paired_bootstrap_95_interval']}; "
            f"fraction with first policy better "
            f"{values['fraction_seeds_a_better']:.2f}"
        )

    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- Lower RMSE is better.",
        "- A negative paired difference favours the first named policy.",
        "- A bootstrap interval is not proof of novelty or generalisation.",
        "- The policies must be checked for implementation correctness before interpreting differences.",
        "- The predictive heuristic is not a trained or calibrated forecasting model.",
        "",
        "## Limitations",
        "",
    ])
    lines.extend([f"- {item}" for item in result["limitations"]])
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")

    print("")
    print("Completed.")
    print(f"Output: {OUT}")
    print(f"Report: {OUT / 'report.md'}")
    print(f"Summary: {OUT / 'summary.json'}")
    print(f"Trials: {csv_path}")
    print(f"Plot: {OUT / 'rmse_comparison.svg'}")

if __name__ == "__main__":
    main()
