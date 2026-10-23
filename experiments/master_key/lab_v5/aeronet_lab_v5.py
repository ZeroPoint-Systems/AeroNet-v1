from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = Path(__file__).resolve().parent / "runs"

AGENTS = 6
STEPS = 300
DT = 1.0
WINDOW = 5
PACKET_LOSS = 0.10
MIN_DELAY = 1
MAX_DELAY = 3
SEEDS = list(range(20261020, 20261040))
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
BASE_R = np.diag([2.0, 2.0])

# Fixed, heterogeneous sensor capabilities. The same sensor model and
# observation availability are used by every policy for a given seed.
SENSOR_SCALES = np.array([0.45, 0.70, 1.0, 1.4, 2.0, 3.0])
OBSERVATION_PROBABILITIES = np.array([0.98, 0.90, 0.80, 0.68, 0.58, 0.48])


def symmetrise(matrix):
    return 0.5 * (matrix + matrix.T)


def predict_state(x, P, count=1):
    x = np.array(x, dtype=float, copy=True)
    P = np.array(P, dtype=float, copy=True)
    for _ in range(count):
        x = F @ x
        P = symmetrise(F @ P @ F.T + Q)
    return x, P


def kalman_update(x, P, observation, R):
    innovation = observation - H @ x
    S = symmetrise(H @ P @ H.T + R)
    K = np.linalg.solve(S, H @ P).T
    updated_x = x + K @ innovation
    A = np.eye(4) - K @ H
    updated_P = symmetrise(A @ P @ A.T + K @ R @ K.T)
    nis = float(innovation.T @ np.linalg.solve(S, innovation))
    return updated_x, updated_P, nis


def covariance_intersection(x1, P1, x2, P2):
    """Conservative track fusion without assuming independent estimates."""
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    P1 = symmetrise(np.asarray(P1, dtype=float))
    P2 = symmetrise(np.asarray(P2, dtype=float))

    for name, x, P in (("first", x1, P1), ("second", x2, P2)):
        if x.shape != (4,) or P.shape != (4, 4):
            raise ValueError(f"Invalid {name} state or covariance shape")
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(P)):
            raise ValueError(f"Non-finite {name} state or covariance")
        try:
            np.linalg.cholesky(P)
        except np.linalg.LinAlgError as exc:
            raise ValueError(f"{name} covariance must be positive definite") from exc

    I1 = np.linalg.solve(P1, np.eye(4))
    I2 = np.linalg.solve(P2, np.eye(4))
    best = None

    for w in np.linspace(0.0, 1.0, 21):
        precision = symmetrise(w * I1 + (1.0 - w) * I2)
        P = symmetrise(np.linalg.solve(precision, np.eye(4)))
        sign, logdet = np.linalg.slogdet(P)
        if sign <= 0 or not np.isfinite(logdet):
            continue
        x = P @ (w * I1 @ x1 + (1.0 - w) * I2 @ x2)
        if best is None or logdet < best[0] - 1e-12:
            best = (logdet, x, P, float(w))

    if best is None:
        raise RuntimeError("Covariance intersection found no valid solution")
    return best[1], best[2]


def make_world(seed):
    rng = np.random.default_rng(seed)
    truth = np.zeros((STEPS, 4), dtype=float)
    truth[0] = [0.0, 0.0, 1.0, -0.4]

    for t in range(1, STEPS):
        truth[t] = F @ truth[t - 1]
        truth[t, 2:] += rng.normal(0.0, 0.12, size=2)

    observations = np.full((STEPS, AGENTS, 2), np.nan, dtype=float)
    for agent_id in range(AGENTS):
        R = BASE_R * SENSOR_SCALES[agent_id]
        for t in range(STEPS):
            if rng.random() < OBSERVATION_PROBABILITIES[agent_id]:
                observations[t, agent_id] = (
                    H @ truth[t] + rng.multivariate_normal(np.zeros(2), R)
                )

    network_rng = np.random.default_rng(seed + 900000)
    loss_draws = network_rng.random((STEPS, AGENTS, AGENTS))
    delay_draws = network_rng.integers(
        MIN_DELAY, MAX_DELAY + 1, size=(STEPS, AGENTS, AGENTS)
    )
    return truth, observations, loss_draws, delay_draws


class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.R = BASE_R * SENSOR_SCALES[agent_id]
        self.x = np.zeros(4, dtype=float)
        self.P = np.diag([20.0, 20.0, 10.0, 10.0])
        self.initialised = False
        self.nis = 0.0
        self.innovation_ema = 1.0
        self.previous_ema = 1.0
        self.risk = 0.0
        self.last_sent_window = -1
        self.observations_used = 0

    def update(self, observation):
        if self.initialised:
            self.x, self.P = predict_state(self.x, self.P)
        elif observation is not None:
            self.x[:2] = observation
            self.x[2:] = 0.0
            self.P = np.diag([
                self.R[0, 0], self.R[1, 1], 10.0, 10.0
            ])
            self.initialised = True
            self.observations_used += 1
            self.nis = 0.0
            self._update_risk()
            return

        if observation is not None:
            if not self.initialised:
                self.initialised = True
            self.x, self.P, self.nis = kalman_update(
                self.x, self.P, observation, self.R
            )
            self.observations_used += 1
        else:
            self.nis = 0.0

        self._update_risk()

    def _update_risk(self):
        self.previous_ema = self.innovation_ema
        self.innovation_ema = (
            0.7 * self.innovation_ema + 0.3 * self.nis
        )
        uncertainty = float(np.trace(self.P[:2, :2]))
        trend = max(0.0, self.innovation_ema - self.previous_ema)
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
    if agent.last_sent_window == window:
        return False

    if policy == "reactive":
        return (
            float(np.trace(agent.P[:2, :2])) > 3.0
            or agent.nis > 5.0
        )
    if policy == "predictive":
        return agent.risk > 1.15

    raise ValueError(f"Unknown policy: {policy}")


def run_trial(seed, policy):
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy: {policy}")

    truth, observations, loss_draws, delay_draws = make_world(seed)
    agents = [Agent(i) for i in range(AGENTS)]
    queue = []
    attempted_broadcasts = 0
    delivered_links = 0
    total_fusions = 0
    state_changing_fusions = 0
    total_fusion_delta = 0.0
    total_covariance_delta = 0.0
    squared_error_sum = 0.0
    error_count = 0

    for t in range(STEPS):
        for i, agent in enumerate(agents):
            raw = observations[t, i]
            observation = raw if np.all(np.isfinite(raw)) else None
            agent.update(observation)

        due = [message for message in queue if message[0] <= t]
        queue = [message for message in queue if message[0] > t]

        for _, sender, receiver, send_time, sent_x, sent_P in due:
            recipient = agents[receiver]
            age = t - send_time
            incoming_x, incoming_P = predict_state(sent_x, sent_P, age)
            before_x = recipient.x.copy()
            before_P = recipient.P.copy()

            recipient.x, recipient.P = covariance_intersection(
                recipient.x, recipient.P, incoming_x, incoming_P
            )

            delta = float(np.linalg.norm(recipient.x - before_x))
            covariance_delta = float(np.linalg.norm(recipient.P - before_P))
            delivered_links += 1
            total_fusions += 1
            total_fusion_delta += delta
            total_covariance_delta += covariance_delta

            if delta > 1e-9 or covariance_delta > 1e-9:
                state_changing_fusions += 1

        estimates = np.array([agent.x[:2] for agent in agents])
        errors = estimates - truth[t, :2]
        squared_error_sum += float(np.sum(errors ** 2))
        error_count += AGENTS

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

                delivery_time = t + int(delay_draws[t, sender, receiver])
                if delivery_time >= STEPS:
                    continue

                queue.append((
                    delivery_time, sender, receiver, t,
                    agent.x.copy(), agent.P.copy()
                ))

    return {
        "seed": int(seed),
        "policy": policy,
        "rmse": math.sqrt(squared_error_sum / error_count),
        "attempted_broadcasts": int(attempted_broadcasts),
        "delivered_links": int(delivered_links),
        "total_fusions": int(total_fusions),
        "state_changing_fusions": int(state_changing_fusions),
        "mean_fusion_state_delta": (
            total_fusion_delta / total_fusions if total_fusions else 0.0
        ),
        "mean_fusion_covariance_delta": (
            total_covariance_delta / total_fusions if total_fusions else 0.0
        ),
        "observations_used": int(sum(a.observations_used for a in agents)),
    }


def mean_sd(values):
    values = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
    }


def paired_comparison(left, right):
    differences = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    mean = float(np.mean(differences))
    if len(differences) > 1:
        se = float(np.std(differences, ddof=1) / np.sqrt(len(differences)))
    else:
        se = 0.0
    return {
        "mean_difference": mean,
        "approx_95_ci": [mean - 1.96 * se, mean + 1.96 * se],
        "n": int(len(differences)),
    }


def run_benchmark():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = OUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)

    results = []
    for seed in SEEDS:
        print(f"Seed {seed}", flush=True)
        for policy in POLICIES:
            results.append(run_trial(seed, policy))

    summary = {}
    for policy in POLICIES:
        rows = [row for row in results if row["policy"] == policy]
        summary[policy] = {
            "rmse": mean_sd([r["rmse"] for r in rows]),
            "attempted_broadcasts": mean_sd(
                [r["attempted_broadcasts"] for r in rows]
            ),
            "delivered_links": mean_sd([r["delivered_links"] for r in rows]),
            "state_changing_fusions": mean_sd(
                [r["state_changing_fusions"] for r in rows]
            ),
            "mean_fusion_state_delta": mean_sd(
                [r["mean_fusion_state_delta"] for r in rows]
            ),
        }

    by_seed = {
        (r["seed"], r["policy"]): r["rmse"] for r in results
    }
    comparisons = {}
    for policy in POLICIES:
        if policy == "none":
            continue
        comparisons[f"{policy}_minus_none"] = paired_comparison(
            [by_seed[(s, policy)] for s in SEEDS],
            [by_seed[(s, "none")] for s in SEEDS],
        )

    payload = {
        "experiment": "AeroNet Lab v4",
        "run_id_utc": run_id,
        "seeds": SEEDS,
        "agents": AGENTS,
        "steps": STEPS,
        "window": WINDOW,
        "packet_loss_probability": PACKET_LOSS,
        "delay_steps": [MIN_DELAY, MAX_DELAY],
        "sensor_scales": SENSOR_SCALES.tolist(),
        "observation_probabilities": OBSERVATION_PROBABILITIES.tolist(),
        "policies": summary,
        "paired_rmse_comparisons": comparisons,
        "interpretation_note": (
            "Exploratory synthetic simulation. Confidence intervals are "
            "normal-approximation intervals over paired seed differences. "
            "They do not establish novelty or external validity."
        ),
    }

    with (out_dir / "trial_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    (out_dir / "summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    lines = [
        "# AeroNet Lab v4 benchmark report",
        "",
        f"Run: `{run_id}` UTC",
        f"Seeds: {len(SEEDS)} paired seeds, {SEEDS[0]} to {SEEDS[-1]}",
        f"Agents: {AGENTS}; steps per trial: {STEPS}",
        "",
        "## Policy results",
        "",
        "| Policy | Mean RMSE | SD RMSE | Mean broadcasts | Mean delivered links | Mean state-changing fusions |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for policy in POLICIES:
        item = summary[policy]
        lines.append(
            f"| {policy} | {item['rmse']['mean']:.6f} | "
            f"{item['rmse']['sd']:.6f} | "
            f"{item['attempted_broadcasts']['mean']:.1f} | "
            f"{item['delivered_links']['mean']:.1f} | "
            f"{item['state_changing_fusions']['mean']:.1f} |"
        )

    lines += ["", "## Paired RMSE comparisons", ""]
    for name, item in comparisons.items():
        lines.append(
            f"- **{name}:** mean difference "
            f"{item['mean_difference']:.6f}, approximate 95% CI "
            f"[{item['approx_95_ci'][0]:.6f}, "
            f"{item['approx_95_ci'][1]:.6f}], n={item['n']}."
        )
    lines += [
        "",
        "Negative policy-minus-none RMSE indicates lower error than no communication.",
        "",
        "## Limitations",
        "",
        "- Synthetic target dynamics and observation model.",
        "- Sensor capabilities are deliberately heterogeneous.",
        "- Covariance intersection is a conservative track-fusion baseline.",
        "- The predictive policy is a hand-designed heuristic, not a trained model.",
        "- Approximate confidence intervals are exploratory; no multiplicity correction is applied.",
        "- No claim of novelty, real-world performance, or causal mechanism is established by this benchmark.",
        "",
    ]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\nPolicy summary")
    for policy in POLICIES:
        item = summary[policy]
        print(
            f"{policy:10s} RMSE={item['rmse']['mean']:.6f} "
            f"SD={item['rmse']['sd']:.6f} "
            f"broadcasts={item['attempted_broadcasts']['mean']:.1f} "
            f"delivered={item['delivered_links']['mean']:.1f} "
            f"changed_fusions={item['state_changing_fusions']['mean']:.1f}"
        )

    print("\nPaired comparisons against none")
    for name, item in comparisons.items():
        print(
            f"{name}: difference={item['mean_difference']:.6f}, "
            f"approximate 95% CI={item['approx_95_ci']}"
        )

    print(f"\nResults written to: {out_dir}")
    return out_dir


if __name__ == "__main__":
    run_benchmark()
