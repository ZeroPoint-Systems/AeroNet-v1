from pathlib import Path

import yaml

from experiments.scientific.adapter import build_config


def test_build_config_applies_scientific_condition(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    output = tmp_path / "generated.yaml"

    base.write_text(
        """
experiment:
  id: base
  seed: 1

sensing:
  measurement_noise: 1.0

communication:
  range: 25.0
  packet_loss_probability: 0.0
  latency: 0.0

swarm:
  number_of_agents: 4
""",
        encoding="utf-8",
    )

    condition = {
        "condition_id": "condition_001",
        "seed": 123,
        "measurement_noise": 2.0,
        "communication_range": 10.0,
        "packet_loss_probability": 0.2,
        "communication_latency": 0.5,
        "number_of_agents": 4,
        "replicate": 0,
        "baseline": "reference_kalman",
    }

    build_config(base, output, condition)

    with output.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["experiment"]["id"] == "condition_001"
    assert config["experiment"]["seed"] == 123
    assert config["sensing"]["measurement_noise"] == 2.0
    assert config["communication"]["range"] == 10.0
    assert config["communication"]["packet_loss_probability"] == 0.2
    assert config["communication"]["latency"] == 0.5
    assert config["swarm"]["number_of_agents"] == 4
