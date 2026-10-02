from __future__ import annotations

from math import hypot
from pathlib import Path

import numpy as np
import yaml

from .model import Agent, Estimate, Observation, Packet, SimulationResult, State2D


def load_config(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML mapping.")

    validate_config(config)
    return config


def validate_config(config: dict) -> None:
    required = ["experiment", "simulation", "target", "swarm", "sensing", "communication"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing configuration sections: {missing}")

    if config["swarm"]["number_of_agents"] < 1:
        raise ValueError("number_of_agents must be >= 1")

    if config["simulation"]["dt"] <= 0:
        raise ValueError("dt must be > 0")

    if config["simulation"]["duration"] <= 0:
        raise ValueError("duration must be > 0")

    noise = config["sensing"]["measurement_noise"]
    if noise < 0:
        raise ValueError("measurement_noise must be >= 0")

    communication = config["communication"]

    if not 0 <= communication.get("packet_loss_probability", 0) <= 1:
        raise ValueError("packet_loss_probability must be between 0 and 1")

    if communication.get("range", 0) < 0:
        raise ValueError("communication.range must be >= 0")

    if communication.get("latency", 0) < 0:
        raise ValueError("communication.latency must be >= 0")


def positions(config: dict) -> list[State2D]:
    explicit = config.get("swarm", {}).get("positions")

    if explicit:
        if len(explicit) != config["swarm"]["number_of_agents"]:
            raise ValueError("Explicit position count does not equal number_of_agents.")
        return [State2D(float(p["x"]), float(p["y"])) for p in explicit]

    radius = float(config["swarm"].get("spawn_radius", 10.0))
    n = config["swarm"]["number_of_agents"]

    if n == 1:
        return [State2D(0.0, 0.0)]

    return [
        State2D(
            radius * np.cos(2 * np.pi * i / n),
            radius * np.sin(2 * np.pi * i / n),
        )
        for i in range(n)
    ]


def run(config: dict) -> SimulationResult:
    seed = int(config["experiment"]["seed"])
    rng = np.random.default_rng(seed)

    dt = float(config["simulation"]["dt"])
    duration = float(config["simulation"]["duration"])
    steps = int(round(duration / dt))

    target = State2D(
        float(config["target"]["x"]),
        float(config["target"]["y"]),
    )

    n = int(config["swarm"]["number_of_agents"])
    sensor_noise = float(config["sensing"]["measurement_noise"])

    comm = config["communication"]
    comm_range = float(comm.get("range", 0))
    loss_probability = float(comm.get("packet_loss_probability", 0))
    latency = float(comm.get("latency", 0))

    initial_covariance = float(
        config.get("estimation", {}).get("initial_covariance", 100.0)
    )

    agents = []

    for i, position in enumerate(positions(config)):
        covariance = np.eye(2) * initial_covariance
        agents.append(
            Agent(
                agent_id=i,
                position=position,
                estimate=Estimate(
                    state=target,
                    covariance=covariance,
                ),
            )
        )

    result = SimulationResult()

    for step in range(steps):
        time = step * dt

        for agent in agents:
            if sensor_noise == 0:
                measured_x = target.x
                measured_y = target.y
            else:
                measured_x = target.x + rng.normal(0, sensor_noise)
                measured_y = target.y + rng.normal(0, sensor_noise)

            observation = Observation(
                agent_id=agent.agent_id,
                time=time,
                truth=target,
                measured=State2D(measured_x, measured_y),
            )

            result.observations.append(observation)

            # Independent local Gaussian measurement update.
            prior = agent.estimate.covariance
            measurement_variance = max(sensor_noise ** 2, 1e-12)
            measurement_covariance = np.eye(2) * measurement_variance

            if sensor_noise == 0:
                estimate_state = target
                posterior = np.eye(2) * 1e-12
            else:
                prior_inverse = np.linalg.inv(prior)
                measurement_inverse = np.linalg.inv(measurement_covariance)

                posterior = np.linalg.inv(
                    prior_inverse + measurement_inverse
                )

                prior_mean = np.array([
                    agent.estimate.state.x,
                    agent.estimate.state.y,
                ])

                measurement_mean = np.array([
                    measured_x,
                    measured_y,
                ])

                posterior_mean = posterior @ (
                    prior_inverse @ prior_mean
                    + measurement_inverse @ measurement_mean
                )

                estimate_state = State2D(
                    float(posterior_mean[0]),
                    float(posterior_mean[1]),
                )

            agent.estimate = Estimate(
                state=estimate_state,
                covariance=posterior,
            )

        # Communication happens after all local updates.
        for sender in agents:
            for receiver in agents:
                if sender.agent_id == receiver.agent_id:
                    continue

                distance = hypot(
                    sender.position.x - receiver.position.x,
                    sender.position.y - receiver.position.y,
                )

                if distance > comm_range:
                    continue

                lost = rng.random() < loss_probability
                delivered = not lost

                result.packets.append(
                    Packet(
                        time_sent=time,
                        time_delivered=time + latency if delivered else None,
                        sender=sender.agent_id,
                        receiver=receiver.agent_id,
                        delivered=delivered,
                        latency=latency if delivered else 0.0,
                        estimate=Estimate(
                            state=sender.estimate.state,
                            covariance=sender.estimate.covariance.copy(),
                        ),
                    )
                )

        for agent in agents:
            dx = agent.estimate.state.x - target.x
            dy = agent.estimate.state.y - target.y
            error = float(np.hypot(dx, dy))

            result.trajectory.append(
                {
                    "step": step,
                    "time": time,
                    "agent_id": agent.agent_id,
                    "truth_x": target.x,
                    "truth_y": target.y,
                    "observation_x": next(
                        o.measured.x
                        for o in reversed(result.observations)
                        if o.agent_id == agent.agent_id
                    ),
                    "observation_y": next(
                        o.measured.y
                        for o in reversed(result.observations)
                        if o.agent_id == agent.agent_id
                    ),
                    "estimate_x": agent.estimate.state.x,
                    "estimate_y": agent.estimate.state.y,
                    "position_error": error,
                    "squared_error": error ** 2,
                    "covariance_trace": agent.estimate.covariance_trace,
                    "covariance_determinant": float(
                        np.linalg.det(agent.estimate.covariance)
                    ),
                }
            )

    return result
