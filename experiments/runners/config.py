"""Experiment configuration loading and validation.

Every value that affects a scientific result is read from a configuration
file, never hard coded in the runner or in simulator modules. This module
is the single place where a configuration file is parsed and checked, so
that a malformed or incomplete configuration fails loudly, before any
simulation time is spent on it, rather than producing a silently wrong
result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigError(ValueError):
    """Raised when a configuration file is missing a required field, or a
    field has a value outside its valid range.
    """


def _require(section: Dict[str, Any], key: str, section_name: str) -> Any:
    if key not in section:
        raise ConfigError(f"missing required field '{key}' in section '{section_name}'")
    return section[key]


@dataclass(frozen=True)
class ExperimentSection:
    id: str
    seed: int


@dataclass(frozen=True)
class SimulationSection:
    dt: float
    duration: float


@dataclass(frozen=True)
class TargetSection:
    x: float
    y: float


@dataclass(frozen=True)
class SwarmSection:
    number_of_agents: int
    spawn_radius: float


@dataclass(frozen=True)
class SensingSection:
    measurement_noise: float


@dataclass(frozen=True)
class CommunicationSection:
    range: float
    packet_loss_probability: float
    latency: float
    enable_fusion: bool


@dataclass(frozen=True)
class EstimationSection:
    method: str
    initial_covariance: float
    process_noise: float


@dataclass(frozen=True)
class Config:
    experiment: ExperimentSection
    simulation: SimulationSection
    target: TargetSection
    swarm: SwarmSection
    sensing: SensingSection
    communication: CommunicationSection
    estimation: EstimationSection
    source_path: Path


_KNOWN_ESTIMATION_METHODS = {"reference_kalman"}


def load_config(path: str) -> Config:
    """Load and validate an experiment configuration file. Raises
    ConfigError with a specific message on any missing or invalid field.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ConfigError(f"configuration file must contain a mapping at the top level: {config_path}")

    experiment_raw = _require(raw, "experiment", "top level")
    simulation_raw = _require(raw, "simulation", "top level")
    target_raw = _require(raw, "target", "top level")
    swarm_raw = _require(raw, "swarm", "top level")
    sensing_raw = _require(raw, "sensing", "top level")
    communication_raw = _require(raw, "communication", "top level")
    estimation_raw = _require(raw, "estimation", "top level")

    experiment = ExperimentSection(
        id=str(_require(experiment_raw, "id", "experiment")),
        seed=int(_require(experiment_raw, "seed", "experiment")),
    )

    dt = float(_require(simulation_raw, "dt", "simulation"))
    duration = float(_require(simulation_raw, "duration", "simulation"))
    if not (math.isfinite(dt) and dt > 0):
        raise ConfigError(f"simulation.dt must be a finite positive number, got {dt!r}")
    if not (math.isfinite(duration) and duration > 0):
        raise ConfigError(f"simulation.duration must be a finite positive number, got {duration!r}")
    simulation = SimulationSection(dt=dt, duration=duration)

    target = TargetSection(
        x=float(_require(target_raw, "x", "target")),
        y=float(_require(target_raw, "y", "target")),
    )

    number_of_agents = int(_require(swarm_raw, "number_of_agents", "swarm"))
    if number_of_agents < 1:
        raise ConfigError(f"swarm.number_of_agents must be at least 1, got {number_of_agents!r}")
    spawn_radius = float(_require(swarm_raw, "spawn_radius", "swarm"))
    if spawn_radius < 0:
        raise ConfigError(f"swarm.spawn_radius must not be negative, got {spawn_radius!r}")
    swarm = SwarmSection(number_of_agents=number_of_agents, spawn_radius=spawn_radius)

    measurement_noise = float(_require(sensing_raw, "measurement_noise", "sensing"))
    if measurement_noise < 0:
        raise ConfigError(f"sensing.measurement_noise must not be negative, got {measurement_noise!r}")
    sensing = SensingSection(measurement_noise=measurement_noise)

    comm_range = float(_require(communication_raw, "range", "communication"))
    if comm_range < 0:
        raise ConfigError(f"communication.range must not be negative, got {comm_range!r}")
    packet_loss_probability = float(_require(communication_raw, "packet_loss_probability", "communication"))
    if not (0.0 <= packet_loss_probability <= 1.0):
        raise ConfigError(
            f"communication.packet_loss_probability must be in [0, 1], got {packet_loss_probability!r}"
        )
    latency = float(_require(communication_raw, "latency", "communication"))
    if latency < 0:
        raise ConfigError(f"communication.latency must not be negative, got {latency!r}")
    enable_fusion = bool(communication_raw.get("enable_fusion", False))
    communication = CommunicationSection(
        range=comm_range,
        packet_loss_probability=packet_loss_probability,
        latency=latency,
        enable_fusion=enable_fusion,
    )

    method = str(_require(estimation_raw, "method", "estimation"))
    if method not in _KNOWN_ESTIMATION_METHODS:
        raise ConfigError(
            f"estimation.method {method!r} is not implemented. "
            f"Known methods: {sorted(_KNOWN_ESTIMATION_METHODS)}"
        )
    initial_covariance = float(_require(estimation_raw, "initial_covariance", "estimation"))
    if initial_covariance <= 0:
        raise ConfigError(f"estimation.initial_covariance must be positive, got {initial_covariance!r}")
    process_noise = float(_require(estimation_raw, "process_noise", "estimation"))
    if process_noise < 0:
        raise ConfigError(f"estimation.process_noise must not be negative, got {process_noise!r}")
    estimation = EstimationSection(
        method=method,
        initial_covariance=initial_covariance,
        process_noise=process_noise,
    )

    if enable_fusion and method == "reference_kalman":
        raise ConfigError(
            "communication.enable_fusion is true, but estimation.method 'reference_kalman' "
            "does not implement peer fusion. See simulation/estimation/reference_kalman.py "
            "and simulation/estimation/covariance_intersection.py."
        )

    return Config(
        experiment=experiment,
        simulation=simulation,
        target=target,
        swarm=swarm,
        sensing=sensing,
        communication=communication,
        estimation=estimation,
        source_path=config_path,
    )
