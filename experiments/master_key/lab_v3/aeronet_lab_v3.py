from __future__ import annotations

import csv
import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SEEDS = list(range(20261020, 20261040))
AGENTS = 6
STEPS = 300
WINDOW = 5
PACKET_LOSS = 0.10
MIN_DELAY = 1
MAX_DELAY = 3
DT = 1.0

POLICIES = ("none", "periodic", "reactive", "predictive")

F = np.array([
    [1.0, 0.0, DT, 0.0],
    [0.0, 1.0, 0.0, DT],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
])

H = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
])

Q = np.diag([0.05, 0.05, 0.08, 0.08])
R = np.diag([2.0, 2.0])


def symmetrise(P):
    return 0.5 * (P + P.T)


def predict_state(x, P, count=1):
    x = np.array(x, dtype=float, copy=True)
    P = np.array(P, dtype=float, copy=True)

    for _ in range(count):
        x = F @ x
        P = symmetrise(F @ P @ F.T + Q)

    return x, P


def kalman_update(x, P, z):
    innovation = z - H @ x
    S = symmetrise(H @ P @ H.T + R)
    K = np.linalg.solve(S, H @ P).T

    x_new = x + K @ innovation
    I = np.eye(4)
    A = I - K @ H
    P_new = symmetrise(A @ P @ A.T + K @ R @ K.T)

    nis = float(innovation.T @ np.linalg.solve(S, innovation))
    return x_new, P_new, nis


def covariance_intersection(x1, P1, x2, P2):
    """Fuse two Gaussian estimates without assuming known cross-correlation."""
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    P1 = symmetrise(np.asarray(P1, dtype=float))
    P2 = symmetrise(np.asarray(P2, dtype=float))

    if x1.shape != (4,) or x2.shape != (4,):
        raise ValueError("State vectors must have shape (4,).")

    if P1.shape != (4, 4) or P2.shape != (4, 4):
        raise ValueError("Covariance matrices must have shape (4, 4).")

    for P in (P1, P2):
        if not np.all(np.isfinite(P)):
            raise ValueError("Covariance contains non-finite values.")
        try:
            np.linalg.cholesky(P)
        except np.linalg.LinAlgError as exc:
            raise ValueError("Covariance must be positive definite.") from exc

    if not np.all(np.isfinite(x1)) or not np.all(np.isfinite(x2)):
        raise ValueError("State vector contains non-finite values.")

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

            x = P @ (
                w * I1 @ x1
                + (1.0 - w) * I2 @ x2
            )

            if best is None or logdet < best[0] - 1e-12:
                best = (logdet, x, P)

        except np.linalg.LinAlgError:
            continue

    if best is None:
        raise RuntimeError("Covariance intersection failed.")

    return best[1], best[2]


def make_world(seed):
    """Generate identical truth and observation data for every policy."""
    rng = np.random.default_rng(seed)

    truth = np.zeros((STEPS, 4), dtype=float)
    truth[0] = [0.0, 0.0, 1.0, -0.4]

    for t in range(1, STEPS):
        truth[t] = F @ truth[t - 1]
        truth[t, 2:] += rng.normal(0.0, 0.12, size=2)

    observations = np.zeros((STEPS, AGENTS, 2), dtype=float)

    for t in range(STEPS):
        for agent_id in range(AGENTS):
            observations[t, agent_id] = (
                H @ truth[t]
                + rng.multivariate_normal(np.zeros(2), R)
            )

    # Pre-generate network conditions so each policy uses the same
    # potential packet outcomes and delays for a given seed and send time.
    network_rng = np.random.default_rng(seed + 900_000)
    loss_draws = network_rng.random((STEPS, AGENTS, AGENTS))
    delay_draws = network_rng.integers(
        MIN_DELAY, MAX_DELAY + 1,
        size=(STEPS, AGENTS, AGENTS),
    )

    return truth, observations, loss_draws, delay_draws


class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.x = np.zeros(4, dtype=float)
        self.P = np.diag([20.0, 20.0, 10.0, 10.0])
        self.initialised = False
        self.nis = 0.0
        self.innovation_ema = 1.0
        self.previous_ema = 1.0
        self.risk = 0.0
        self.last_sent_window = -1

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

        uncertainty = float(np.trace(self.P[:2, :2]))
        trend = max(0.0, self.innovation_ema - self.previous_ema)

        # Exploratory heuristic only, not a trained predictive model.
        self.risk = (
            0.50 * min(4.0, uncertainty / 2.0)
            + 0.35 * min(4.0, self.innovation_ema / 2.0)
            + 0.15 * min(4.0, trend * 2.0)
        )


def should_send(policy, agent, t):
    if policy == "none":
        return False

    if policy == "periodic":
        return t % WINDOW == 0

    window = t // WINDOW
    window_end = min((window + 1) * WINDOW - 1, STEPS - 1)

    if agent.last_sent_window == window:
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

    # Guarantee one broadcast per agent per complete window.
    return trigger or t == window_end


def run_trial(seed, policy):
    truth, observations, loss_draws, delay_draws = make_world(seed)
    agents = [Agent(i) for i in range(AGENTS)]

    # Each message contains:
    # (delivery_time, sender, receiver, send_time, state, covariance)
    queue = []

    attempted_broadcasts = 0
    delivered_links = 0
    state_changing_fusions = 0
    total_fusion_delta = 0.0
    total_fusions = 0
    error_squares = []
    peak_queue = 0

    for t in range(STEPS):
        # 1. Every agent performs its own observation update.
        for i, agent in enumerate(agents):
            agent.update(observations[t, i])

        # 2. Deliver all messages whose delivery time has arrived.
        due = [message for message in queue if message[0] <= t]
        queue = [message for message in queue if message[0] > t]

        for _, sender, receiver, send_time, sent_x, sent_P in due:
            receiver_agent = agents[receiver]
            age = t - send_time

            incoming_x, incoming_P = predict_state(
                sent_x, sent_P, age
            )

            before_x = receiver_agent.x.copy()
            before_P = receiver_agent.P.copy()

            receiver_agent.x, receiver_agent.P = covariance_intersection(
                receiver_agent.x,
                receiver_agent.P,
                incoming_x,
                incoming_P,
            )

            delta = float(np.linalg.norm(receiver_agent.x - before_x))
            covariance_delta = float(
                np.linalg.norm(receiver_agent.P - before_P)
            )

            delivered_links += 1
            total_fusions += 1
            total_fusion_delta += delta

            if delta > 1e-9 or covariance_delta > 1e-9:
                state_changing_fusions += 1

        # 3. Schedule broadcasts after local updates and deliveries.
        for sender, agent in enumerate(agents):
            if not should_send(policy, agent, t):
                continue

            attempted_broadcasts += 1
            agent.last_sent_window = t // WINDOW

            for receiver in range(AGENTS):
                if receiver == sender:
                    continue

                if loss_draws[t, sender, receiver] < PACKET_LOSS:
                    continue

                delay = int(delay_draws[t, sender, receiver])
                delivery_time = t + delay

                queue.append((
                    delivery_time,
                    sender,
                    receiver,
                    t,
                    agent.x.copy(),
                    agent.P.copy(),
                ))

        peak_queue = max(peak_queue, len(queue))

        # 4. Evaluate every agent against the known truth at this time.
        # The metric is computed after all deliveries at this time.
        for agent in agents:
            error = agent.x[:2] - truth[t, :2]
            error_squares.append(float(error @ error))

    rmse = math.sqrt(float(np.mean(error_squares)))
    attempted_links = attempted_broadcasts * (AGENTS - 1)

    return {
        "seed": seed,
        "policy": policy,
        "rmse": rmse,
        "attempted_broadcasts": attempted_broadcasts,
        "attempted_links": attempted_links,
        "delivered_links": delivered_links,
        "delivery_rate": (
            delivered_links / attempted_links
            if attempted_links else 0.0
        ),
        "state_changing_fusions": state_changing_fusions,
        "mean_fusion_state_delta": (
            total_fusion_delta / total_fusions
            if total_fusions else 0.0
        ),
        "pending_messages_at_end": len(queue),
        "peak_queue": peak_queue,
    }


def run_campaign():
    rows = []

    for seed in SEEDS:
        for policy in POLICIES:
            rows.append(run_trial(seed, policy))

    return rows


def summarise(rows):
    summary = {}

    for policy in POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        values = np.array([row["rmse"] for row in selected])

        summary[policy] = {
            "n": len(selected),
            "mean_rmse": float(np.mean(values)),
            "sd_rmse": float(np.std(values, ddof=1)),
            "mean_attempted_broadcasts": float(np.mean([
                row["attempted_broadcasts"] for row in selected
            ])),
            "mean_delivered_links": float(np.mean([
                row["delivered_links"] for row in selected
            ])),
            "mean_delivery_rate": float(np.mean([
                row["delivery_rate"] for row in selected
            ])),
            "mean_state_changing_fusions": float(np.mean([
                row["state_changing_fusions"] for row in selected
            ])),
            "mean_fusion_state_delta": float(np.mean([
                row["mean_fusion_state_delta"] for row in selected
            ])),
        }

    # Paired differences use the same seed for each policy pair.
    comparisons = {}
    by_key = {(row["seed"], row["policy"]): row for row in rows}

    for policy in POLICIES:
        if policy == "none":
            continue

        differences = np.array([
            by_key[(seed, policy)]["rmse"]
            - by_key[(seed, "none")]["rmse"]
            for seed in SEEDS
        ])

        # Approximate paired 95% interval using a normal critical value.
        mean_diff = float(np.mean(differences))
        standard_error = float(
            np.std(differences, ddof=1) / math.sqrt(len(differences))
        )

        comparisons[f"{policy}_minus_none"] = {
            "mean_rmse_difference": mean_diff,
            "approx_95_ci_low": mean_diff - 1.96 * standard_error,
            "approx_95_ci_high": mean_diff + 1.96 * standard_error,
            "fraction_seeds_policy_better": float(
                np.mean(differences < 0.0)
            ),
        }

    return {
        "experiment": {
            "name": "AeroNet Lab v3 validation benchmark",
            "synthetic_data": True,
            "seeds": SEEDS,
            "agents": AGENTS,
            "steps": STEPS,
            "window": WINDOW,
            "packet_loss_probability": PACKET_LOSS,
            "delay_steps": [MIN_DELAY, MAX_DELAY],
            "policies": list(POLICIES),
            "metric": (
                "RMSE of each agent's estimated position against "
                "synthetic ground truth, after deliveries at each step"
            ),
        },
        "policy_summary": summary,
        "paired_comparisons_against_none": comparisons,
        "limitations": [
            "Synthetic constant-velocity model with stochastic acceleration.",
            "All agents observe the same target, with independent sensor noise.",
            "The predictive policy is a fixed heuristic, not a trained predictor.",
            "Pairwise covariance intersection is applied repeatedly; "
            "cross-correlation handling requires further study.",
            "The paired confidence intervals are approximate.",
            "This is not a real-drone or real-dataset validation.",
        ],
    }


def write_outputs(rows, report):
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = ROOT / "runs" / run_id
    out.mkdir(parents=True, exist_ok=False)

    csv_path = out / "trial_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with (out / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    lines = [
        "# AeroNet Lab v3 validation benchmark",
        "",
        "This is an exploratory synthetic simulation, not real-world validation.",
        "",
        f"- Paired seeds: {len(SEEDS)}",
        f"- Agents: {AGENTS}",
        f"- Steps per trial: {STEPS}",
        f"- Packet loss probability per link: {PACKET_LOSS:.0%}",
        f"- Delay: {MIN_DELAY}-{MAX_DELAY} steps",
        "",
        "## Results",
        "",
        "| Policy | Mean RMSE | SD RMSE | Mean broadcasts | Mean delivered links | State-changing fusions |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for policy, item in report["policy_summary"].items():
        lines.append(
            f"| {policy} | {item['mean_rmse']:.6f} "
            f"| {item['sd_rmse']:.6f} "
            f"| {item['mean_attempted_broadcasts']:.1f} "
            f"| {item['mean_delivered_links']:.1f} "
            f"| {item['mean_state_changing_fusions']:.1f} |"
        )

    lines.extend([
        "",
        "## Paired RMSE differences against no communication",
        "",
        "Negative differences favour the communication policy.",
        "",
        "| Comparison | Mean difference | Approximate 95% interval | Seeds improved |",
        "|---|---:|---:|---:|",
    ])

    for name, item in report["paired_comparisons_against_none"].items():
        lines.append(
            f"| {name} | {item['mean_rmse_difference']:.6f} "
            f"| [{item['approx_95_ci_low']:.6f}, "
            f"{item['approx_95_ci_high']:.6f}] "
            f"| {item['fraction_seeds_policy_better']:.0%} |"
        )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A non-zero fusion count shows that received messages changed an "
        "estimate or covariance. It does not by itself demonstrate improved "
        "accuracy. Compare RMSE, delivery rate and communication cost together.",
        "",
    ])

    (out / "report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    return out


def main():
    print("Running AeroNet Lab v3 validation benchmark...")
    rows = run_campaign()
    report = summarise(rows)
    out = write_outputs(rows, report)

    print(f"\nResults written to: {out}")
    print("\nPolicy summary:")

    for policy, item in report["policy_summary"].items():
        print(
            f"{policy:10s} "
            f"RMSE={item['mean_rmse']:.6f} "
            f"SD={item['sd_rmse']:.6f} "
            f"broadcasts={item['mean_attempted_broadcasts']:.1f} "
            f"delivered={item['mean_delivered_links']:.1f} "
            f"changed_fusions={item['mean_state_changing_fusions']:.1f}"
        )

    print("\nPaired comparisons against none:")
    for name, item in report["paired_comparisons_against_none"].items():
        print(
            f"{name}: difference={item['mean_rmse_difference']:.6f}, "
            f"approximate 95% CI="
            f"[{item['approx_95_ci_low']:.6f}, "
            f"{item['approx_95_ci_high']:.6f}]"
        )


if __name__ == "__main__":
    main()
