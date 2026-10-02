from pathlib import Path

from aeronet_research.batch import expand_grid
from aeronet_research.io import stable_seed
from aeronet_research.simulation import load_config


def test_grid_expansion():
    runs = list(
        expand_grid(
            {
                "a": [1, 2],
                "b": [10, 20],
            }
        )
    )

    assert len(runs) == 4


def test_seed_reproducibility():
    assert stable_seed(123, 0) == stable_seed(123, 0)
    assert stable_seed(123, 0) != stable_seed(123, 1)


def test_config_loads():
    config = load_config(
        Path("experiments/configs/research_validation.yaml")
    )

    assert config["swarm"]["number_of_agents"] == 4


def test_required_data_schema():
    expected = {
        "experiment",
        "simulation",
        "target",
        "swarm",
        "sensing",
        "communication",
    }

    config = load_config(
        Path("experiments/configs/research_validation.yaml")
    )

    assert expected.issubset(config)
