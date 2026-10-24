import numpy as np

from .estimator import LocalKalmanFilter
from .model import measurement_matrix, simulate_truth
from .network import CommunicationNetwork
from .policies import build_policies


def _binary_metrics(predicted, actual):
    predicted = np.asarray(predicted, dtype=bool)
    actual = np.asarray(actual, dtype=bool)

    tp = int(np.sum(predicted & actual))
    fp = int(np.sum(predicted & ~actual))
    fn = int(np.sum(~predicted & actual))
    tn = int(np.sum(~predicted & ~actual))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": fpr,
    }


def run_trial(config, seed, policy_name):
    # Independent seeded streams make truth and local measurements paired
    # across policies. The network schedule is also identical for each policy.
    truth = simulate_truth(
        config, np.random.default_rng(seed + 10_000_019)
    )
    meas_rngs = [
        np.random.default_rng(seed + 1000 + i)
        for i in range(config.agents)
    ]
    network = CommunicationNetwork(config, seed + 20_000_033)
    H = measurement_matrix()

    filters = [
        LocalKalmanFilter(
            config.dt, config.process_noise, config.measurement_noise
        )
        for _ in range(config.agents)
    ]

    policies = {p.name: p for p in build_policies(config)}
    if policy_name not in policies:
        raise ValueError(f"Unknown policy: {policy_name}")
    policy = policies[policy_name]

    pending = [[] for _ in range(config.steps)]
    errors = np.zeros((config.steps, config.agents), dtype=float)
    warning = np.zeros((config.steps, config.agents), dtype=bool)

    # Independent warning tracker, evaluated in every policy trial.
    # It predicts future estimation error, not merely future innovation.
    predictor_previous = np.zeros(config.agents)
    predictor_trend = np.zeros(config.agents)

    for step in range(config.steps):
        measurements = [
            H @ truth[step] + meas_rngs[i].normal(
                0.0, np.sqrt(config.measurement_noise), size=2
            )
            for i in range(config.agents)
        ]

        for filt in filters:
            filt.predict()
        for i, filt in enumerate(filters):
            filt.update(measurements[i])

        # Deliver messages that arrived at this step exactly once.
        inbox = [[] for _ in range(config.agents)]
        for receiver, sender, state, sent_step in pending[step]:
            if network.active[step, receiver]:
                network.delivered += 1
                inbox[receiver].append(
                    (state, step - sent_step)
                )
            else:
                network.dropped += 1

        for i, messages in enumerate(inbox):
            fresh = [
                state for state, age in messages
                if age <= max(1, config.max_delay)
            ]
            filters[i].consensus(fresh)

        # Calculate the warning signal independently of the communication
        # policy, so warning evaluation is available for every policy run.
        for i, filt in enumerate(filters):
            score = float(filt.innovation_norm)
            trend = (
                0.75 * predictor_trend[i]
                + 0.25 * (score - predictor_previous[i])
            )
            predictor_trend[i] = trend
            predictor_previous[i] = score
            predicted_score = max(
                0.0, score + config.prediction_horizon * trend
            )
            warning[step, i] = (
                predicted_score >= config.warning_threshold
            )

        # One policy decision attempts at most one packet to one ring
        # neighbour. The budget therefore counts individual packet attempts.
        for i, filt in enumerate(filters):
            if policy.decide(i, step, filt):
                neighbours = network.neighbours(i)
                receiver = neighbours[int(policy.used[i]) % len(neighbours)]
                network.transmit(step, i, receiver, filt.x, pending)
                policy.record(i, step)

        for i, filt in enumerate(filters):
            errors[step, i] = np.linalg.norm(
                filt.x[:2] - truth[step, :2]
            )

    horizon = config.degradation_horizon
    if config.steps > horizon:
        future_max = np.asarray([
            np.max(errors[t + 1:t + horizon + 1], axis=0)
            for t in range(config.steps - horizon)
        ])
        actual = future_max >= config.degradation_threshold
        predicted = warning[:config.steps - horizon]
        warning_metrics = _binary_metrics(predicted, actual)
    else:
        warning_metrics = _binary_metrics(
            np.zeros((0, config.agents), dtype=bool),
            np.zeros((0, config.agents), dtype=bool),
        )

    if not np.all(policy.used <= policy.budget):
        raise RuntimeError("Policy exceeded its per-agent packet budget")

    if network.sent != network.delivered + network.dropped:
        raise RuntimeError(
            "Packet accounting inconsistent: "
            f"sent={network.sent}, delivered={network.delivered}, "
            f"dropped={network.dropped}"
        )

    return {
        "seed": int(seed),
        "policy": policy_name,
        "position_rmse": float(np.sqrt(np.mean(errors ** 2))),
        "mean_position_error": float(np.mean(errors)),
        "messages_sent": int(network.sent),
        "bytes_sent": int(network.bytes_sent),
        "messages_delivered": int(network.delivered),
        "messages_dropped": int(network.dropped),
        "per_agent_budget_used": policy.used.tolist(),
        "warning_metrics": warning_metrics,
        "step_mean_errors": np.mean(errors, axis=1).tolist(),
    }
