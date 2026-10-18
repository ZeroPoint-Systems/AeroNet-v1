"""The experiment runner.

Wires together the world, swarm, sensing, communication and estimation
layers according to a configuration file, executes the simulation, and
writes a complete, self describing experiment record: the configuration
used, the software and hardware context, the trajectory of every agent's
local estimate, the resulting metrics, and a manifest tying all of that
together with the experiment's unique ID and the git commit it was run
under.

This module contains no scientific logic of its own. It only sequences
calls into simulation/ and analysis/metrics/, in the order set out in
simulation/README.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from analysis.metrics.covariance import covariance_trace
from analysis.metrics.estimation_error import position_error, rmse
from experiments.runners.config import Config, load_config
from simulation.communication.channel import Channel
from simulation.communication.graph import CommunicationGraph
from simulation.communication.latency import FixedLatencyModel
from simulation.communication.packet_loss import PacketLossModel
from simulation.core.agent import Agent
from simulation.core.state import State2D
from simulation.core.swarm import Swarm
from simulation.core.time import SimulationClock
from simulation.core.world import World
from simulation.estimation.reference_kalman import ReferenceKalmanFilter
from simulation.sensing.observation_model import DirectGaussianObservationModel

REPO_ROOT = Path(__file__).resolve().parents[2]
SOFTWARE_VERSION = "0.1.0"


def _git_commit() -> str:
    """The current git commit hash, or the literal string 'unknown' if this
    is not a git repository or has no commits yet. Never fabricated.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def build_world_and_agents(config: Config, rng_positions: np.random.Generator) -> World:
    """Build the World and its Swarm from a validated configuration.

    ASSUMPTION: agents are spawned uniformly at random within a square of
    half width swarm.spawn_radius, centred on the origin, independent of
    the target location. Agents do not move in sprint 1, so this initial
    placement is fixed for the whole run.
    """
    swarm = Swarm()
    for i in range(config.swarm.number_of_agents):
        agent_id = f"agent_{i:03d}"
        offset = rng_positions.uniform(
            low=-config.swarm.spawn_radius, high=config.swarm.spawn_radius, size=2
        )
        position = State2D(x=float(offset[0]), y=float(offset[1]))
        estimator = ReferenceKalmanFilter(
            initial_mean=np.zeros(2),
            initial_covariance=np.eye(2) * config.estimation.initial_covariance,
            process_noise_covariance=np.eye(2) * config.estimation.process_noise,
        )
        swarm.add_agent(Agent(agent_id=agent_id, position=position, estimator=estimator))

    clock = SimulationClock(dt=config.simulation.dt)
    return World(
        true_target_state=State2D(x=config.target.x, y=config.target.y),
        swarm=swarm,
        clock=clock,
    )


def run_simulation(config: Config) -> Dict[str, Any]:
    """Execute one complete simulation run and return the raw trajectory
    and communication statistics needed to write the experiment record.
    Does not touch the filesystem.
    """
    seed_sequence = np.random.SeedSequence(config.experiment.seed)
    seed_positions, seed_noise, seed_channel = seed_sequence.spawn(3)
    rng_positions = np.random.default_rng(seed_positions)
    rng_noise = np.random.default_rng(seed_noise)
    rng_channel = np.random.default_rng(seed_channel)

    world = build_world_and_agents(config, rng_positions)

    observation_model = DirectGaussianObservationModel(
        measurement_covariance=np.eye(2) * config.sensing.measurement_noise,
        rng=rng_noise,
    )
    channel = Channel(
        packet_loss_model=PacketLossModel(
            loss_probability=config.communication.packet_loss_probability, rng=rng_channel
        ),
        latency_model=FixedLatencyModel(latency=config.communication.latency),
    )

    number_of_steps = int(round(config.simulation.duration / config.simulation.dt))
    trajectory: List[Dict[str, Any]] = []

    for _ in range(number_of_steps):
        world.step()
        current_time = world.clock.time

        for agent in world.swarm.active_agents():
            agent.predict(config.simulation.dt)
            observation = observation_model.observe(
                agent_id=agent.agent_id,
                agent_position=agent.position,
                true_state=world.true_target_state,
                timestamp=current_time,
            )
            agent.receive_observation(observation)

        graph = CommunicationGraph(
            world.swarm.active_agents(), communication_range=config.communication.range
        )
        for agent in world.swarm.active_agents():
            payload = {
                "mean": agent.estimate.tolist(),
                "covariance": agent.covariance.tolist(),
            }
            for neighbour_id in graph.neighbours(agent.agent_id):
                channel.send(
                    sender_id=agent.agent_id,
                    receiver_id=neighbour_id,
                    payload=payload,
                    created_time=current_time,
                    graph=graph,
                )

        delivered = channel.collect_deliverable(current_time=current_time)
        for packet in delivered:
            if config.communication.enable_fusion:
                receiver = world.swarm.get_agent(packet.receiver_id)
                mean = np.array(packet.payload["mean"])
                covariance = np.array(packet.payload["covariance"])
                receiver.receive_peer_estimate(packet.sender_id, mean, covariance)
            # If fusion is disabled, the packet has still been generated,
            # subjected to loss and latency, and delivered. Its content is
            # simply not incorporated into the estimator. This exercises
            # the full communication pipeline honestly, without pretending
            # that an unresolved fusion rule has been chosen.

        for agent in world.swarm.active_agents():
            error = position_error(agent.estimate, world.true_target_state.as_array())
            trajectory.append(
                {
                    "step": world.clock.step_index,
                    "time": current_time,
                    "agent_id": agent.agent_id,
                    "estimate_x": float(agent.estimate[0]),
                    "estimate_y": float(agent.estimate[1]),
                    "position_error": error,
                    "covariance_trace": covariance_trace(agent.covariance),
                }
            )

    packet_loss_model = channel._packet_loss_model  # internal, read only, for reporting
    communication_stats = {
        "packets_generated": packet_loss_model.generated_count,
        "packets_delivered": packet_loss_model.delivered_count,
        "packets_lost": packet_loss_model.lost_count,
        "realised_loss_rate": packet_loss_model.realised_loss_rate(),
    }

    return {"trajectory": trajectory, "communication_stats": communication_stats}


def _compute_metrics(trajectory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per agent RMSE and final covariance trace, computed from the raw
    trajectory. These are candidate diagnostic metrics, not the final
    boundary criterion; see analysis/boundary_estimation.
    """
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for row in trajectory:
        by_agent.setdefault(row["agent_id"], []).append(row)

    metrics_rows = []
    for agent_id, rows in sorted(by_agent.items()):
        errors = [r["position_error"] for r in rows]
        metrics_rows.append(
            {
                "agent_id": agent_id,
                "rmse": rmse(errors),
                "final_covariance_trace": rows[-1]["covariance_trace"],
                "number_of_steps": len(rows),
            }
        )
    return metrics_rows


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty CSV file: {path}")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(config_path: str, output_root: Path = REPO_ROOT / "experiments" / "raw") -> Path:
    """Run one experiment end to end and write its complete record.

    Raises FileExistsError if the experiment ID has already been used,
    since raw experimental output is immutable and must never be
    overwritten. Raises ConfigError, from experiments.runners.config, if
    the configuration file is invalid.
    """
    config = load_config(config_path)
    output_dir = Path(output_root) / config.experiment.id
    if output_dir.exists():
        raise FileExistsError(
            f"experiment id {config.experiment.id!r} already has raw output at {output_dir}; "
            "raw data is immutable, choose a new experiment id"
        )

    result = run_simulation(config)
    trajectory = result["trajectory"]
    metrics_rows = _compute_metrics(trajectory)

    output_dir.mkdir(parents=True, exist_ok=False)

    with open(config.source_path, "r") as f:
        config_text = f.read()
    (output_dir / "config.yaml").write_text(config_text)

    timestamp_utc = datetime.now(timezone.utc).isoformat()
    git_commit = _git_commit()

    metadata = {
        "timestamp_utc": timestamp_utc,
        "git_commit": git_commit,
        "software_version": SOFTWARE_VERSION,
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    _write_csv(output_dir / "trajectory.csv", trajectory)
    _write_csv(output_dir / "metrics.csv", metrics_rows)

    manifest = {
        "experiment_id": config.experiment.id,
        "git_commit": git_commit,
        "configuration": config.source_path.name,
        "seed": config.experiment.seed,
        "hardware_version": "not_applicable_simulation_only",
        "software_version": SOFTWARE_VERSION,
        "timestamp_utc": timestamp_utc,
        "dataset": {
            "trajectory": "trajectory.csv",
            "metrics": "metrics.csv",
        },
        "communication_stats": result["communication_stats"],
        "status": "complete",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    manifests_dir = REPO_ROOT / "experiments" / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    (manifests_dir / f"{config.experiment.id}.json").write_text(json.dumps(manifest, indent=2))

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single AeroNet experiment from a configuration file.")
    parser.add_argument("--config", required=True, help="path to an experiment configuration YAML file")
    args = parser.parse_args()
    output_dir = run(args.config)
    print(f"experiment complete, output written to {output_dir}")


if __name__ == "__main__":
    main()
